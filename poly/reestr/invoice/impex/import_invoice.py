""" invoice XML file import class definition """

import os
import xml.etree.cElementTree as ET
#from datetime import datetime
#from typing import Tuple, List, Dict
from pathlib import Path
from zipfile import ZipFile
from psycopg2 import sql as psy_sql
from poly.reestr.invoice.impex import config
from poly.reestr.invoice.impex.utils import get_text, tmp_table_name


class XmlImport:

    def __init__(self, sql: object, zipfile: str, typ: int, _ar: str):
        """
            @param: zipfile: str - abs path to the zip file of invoice
            @param: sql: context manager of the DB SqlProvider
            @praram: typ: int type of the invoce
            @param: _ar: str 2 last digits of the year

        """
        zip_fwd= Path(zipfile)
        self.zip_dir= zip_fwd.parent
        self.zip_file= zip_fwd.name

        self.sql = sql
        self.qurs = sql.qurs

        self.typ = typ
        self._ar = _ar

        self.zap= (
            'n_zap',
            ('pacient', ('id_pac', 'spolis', 'npolis', 'enp' ),),
            ('z_sl', (
                'usl_ok', 'vidpom', 'for_pom', 'date_z_1', 'date_z_2', 'rslt', 'ishod',
                ('sl', ( 'profil', 'nhistory', 'ds1', 'prvs',)),
                'idsp', 'sumv', 'sump',
            ))
        )
        self.pers= ( 'id_pac', 'fam', 'im', 'ot', 'w', 'dr')
        self.zp_tags = ('ZAP', 'PERS',)
        self.meta= {}

        self.usl= (
            ('PROFIL', int), ('CODE_USL', str),
            ('KOL_USL', lambda s: int(s.split('.')[0])),
            ('TARIF', str), ('PRVS', int)
        )
        self.pmu_rec= ('KOL_USL', 'TARIF', 'PROFIL', 'PRVS', )



    # TODO here may be generator yelding text chunk
    def read_zp(self, elem: ET.Element, tags: tuple, rec: list):
        """ recurcively read the tags tuple, find match one in the Etree
            and add the text node of the match tag to the rec list
        """
        for tag in tags:
            if isinstance(tag, tuple):
                _el= elem.find( tag[0].upper() )
                self.read_zp(_el, tag[1], rec ) # yeld from read_zp
            else:
                rec.append( get_text(elem, tag.upper()) ) #yeld get_text


    def write_zp(self, rec: list, tag: str):
        """ write the rec to the DB table
        """
        if tag == 'ZAP':
            self.qurs.execute(self.insert_zap, rec)
        else:
            # first el is 'id_pac' skip it
            rec.append( rec.pop(0) )
            self.qurs.execute(self.insert_pers, rec)


    def parse_xml(self, xml_file: str, tags: tuple):
        context = ET.iterparse(xml_file)
        for _, elem in context:
            rec= []
            if elem.tag not in self.zp_tags:
                # skip non ZAP/PERS tags
                continue
            self.read_zp(elem, tags, rec)
            self.write_zp(rec, elem.tag)


    def set_mek(self):
        """ set mek flag """

        self.qurs.execute(config.GET_MEK_TABLE, ( int(self._ar),) )
        _t = self.qurs.fetchone()

        # mek is not processed yet (not in if)
        if not _t is None:
            return 0, 0
        mek_read, mek_write = 0, 0
        set_mek= (config.SET_MEK % self._ar) + '%s;'

        self.qurs.execute(psy_sql.SQL(config.GET_MEK_TMP).format(self.inv_table))
        for row in self.qurs.fetchall():
            # read mek
            mek_read += 1
            try:
                self.qurs.execute(set_mek, row)
                # write mek
                mek_write += 1
            except Exception as exc:
                raise exc

        return mek_read, mek_write


    def unzip_invoice(self):
        _hm = ''
        os.chdir(self.zip_dir)
        with ZipFile(self.zip_file) as zfile:
            for _nz in zfile.namelist():
                if _nz.startswith('HM') or _nz.startswith('CM') or _nz.startswith('DOM'):
                    zfile.extract(_nz)
                    _hm= _nz
                    _c1= _nz[0]
                    if _c1 in('H', 'D'):
                        _lm= _nz.replace(_c1, 'L')
                    else:
                        _lm= _nz.replace(_c1, 'LC')
                    zfile.extract(_lm)
        return _hm, _lm


    def invoice(self) -> tuple:
        """ returns tuple of 1 if any errors occured
            else records count and meta info
        """

        _hm, _lm = self.unzip_invoice()

        if len(_hm) == 0:
            #bad invoice file name
            return ((1, 0), False)

        # import PMUs with tarifs
        if self.typ == 6:
            return self.pmus(_hm, _lm)

        self.inv_table = tmp_table_name()
        self.qurs.execute(
            psy_sql.SQL(config.CREATE_TBL_INV).format(self.inv_table)
        )
        self.insert_zap = psy_sql.SQL(config.INS_INV_TMP).format(self.inv_table)
        self.insert_pers = psy_sql.SQL(config.PERSQ_TMP).format(self.inv_table)

        #self.qurs.execute(config.TRUNC_TBL_INV)
        #self.sql.db.commit()

        # 2. process files
        # ---------------------------------------------
        for (file, record) in ( (_hm, self.zap), (_lm, self.pers)):
            self.parse_xml(file, record)
            self.sql._db.commit()

        _, mekw = self.set_mek()
        #print(f'MEK invoice: {mekr} talonz: {mekw}')

        # set temp invoice table name for DB session
        setattr(self.sql, 'inv_table', self.inv_table)
        self.qurs.execute(
            psy_sql.SQL(config.COUNT_INV_TMP).format(self.inv_table)
        )

        return self.close(_hm, _lm, self.qurs.fetchone(), mekw)


    def parse_usl(self, elem: ET.Element) -> dict:
        usl= dict()
        for tag, fn in self.usl:
            try:
                usl[tag]= fn( get_text(elem, tag) )
            except:
                usl[tag]= None
        return usl


    def pmus(self, _hm: str, _lm: str) -> tuple:
        pmu= dict()

        context = ET.iterparse(_hm)
        for _, elem in context:
            if elem.tag == 'USL':
                usl= self.parse_usl(elem)

                if pmu.get( usl['CODE_USL'], None ) is None:
                    # no such code in PMUs yet, then init this key
                    pmu[ usl['CODE_USL'] ]= [ usl[ tag ] for tag in self.pmu_rec]
                else:
                    # already have, then add in total
                    pmu[ usl['CODE_USL'] ][0] += usl['KOL_USL']

        usl_table = tmp_table_name()
        self.qurs.execute(
            psy_sql.SQL(config.CREATE_TBL_USL).format(usl_table)
        )
        self.sql._db.commit()

        for key in pmu.keys():
            try:
                rec= [key]
                rec.extend ( pmu[key] )
                self.qurs.execute(psy_sql.SQL(config.INS_USL_TMP).format(usl_table), rec)
            except Exception as exc:
                raise exc

            self.sql._db.commit()

        setattr(self.sql, 'usl_table', usl_table)
        self.qurs.execute(psy_sql.SQL(config.COUNT_USL_TMP).format(usl_table))

        return self.close(_hm, _lm, self.qurs.fetchone(), 0)


    def close(self, _hm: str, _lm: str, recs: tuple, corrected: int) -> tuple:
        os.remove(_hm)
        os.remove(_lm)
        self.sql._db.commit()

        # return signature
        # ( ( rows_of_imported, rows_of_corrected ), done_status)
        return ((recs[0], corrected), True) if recs and len(recs) > 0 else ((2, 0), False)
