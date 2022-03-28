import os, types
import xml.etree.cElementTree as ET
#from datetime import datetime
#from typing import Tuple, List, Dict
from pathlib import Path
from zipfile import ZipFile
from psycopg2 import sql
from poly.reestr.invoice.impex import config
from poly.reestr.invoice.impex.utils import get_text, tmp_table_name
from poly.reestr.invoice.impex.imp_usl import imp_usl

sn= types.SimpleNamespace(
    zap= (
        'n_zap',
        ('pacient', ('id_pac', 'spolis', 'npolis' ),),
        ('z_sl', (
            'usl_ok', 'vidpom', 'for_pom', 'date_z_1', 'date_z_2', 'rslt', 'ishod',
            ('sl', ( 'profil', 'nhistory', 'ds1', 'prvs',)),
            'idsp', 'sumv', 'sank_it',
        ))
    ),

    pers= ( 'id_pac', 'fam', 'im', 'ot', 'w', 'dr'),

    zp_tags = ('ZAP', 'PERS',),

    meta= {}
 )

# here may be generator yelding next text chunk
def get_zp(elem: ET.Element, tags: tuple, rec: list):
    for t in tags:
        if isinstance(t, tuple):
            e= elem.find( t[0].upper() )
            get_zp(e, t[1], rec ) # yeld from get_zp
        else:
            rec.append( get_text(elem, t.upper()) ) #yeld get_text

def set_zp(rec: list, upd: str): # -> None:
    global sn
    if upd == 'ZAP':
        #sn.qurs.execute(config.INS_INV, rec)
        sn.qurs.execute(sn.insert_inv, rec)
    else:
        # first el is id_pac
        rec.append( rec.pop(0) )
        #sn.qurs.execute(config.PERSQ, rec)
        sn.qurs.execute(sn.insert_pers, rec)

def zp_xml(xml: str, tags: tuple):
    global sn
    context = ET.iterparse(xml)
    for _, elem in context:
        rec= list()

        if elem.tag not in sn.zp_tags:
            continue
        get_zp(elem, tags, rec)
        set_zp(rec, elem.tag)

def set_mek(ar):
    # ar - 2 last digits of year
    global sn
    # set mek flag
    sn.qurs.execute(config.GET_MEK_TABLE, ( int(ar),) )
    t= sn.qurs.fetchone()
    if t is None:
        return 0
    mr = 0
    sn.qurs.execute(sql.SQL(config.GET_MEK_TMP).format(sn.inv_table))

    set_mek= (config.SET_MEK % ar) + '%s;'
    for row in sn.qurs.fetchall():
        sn.qurs.execute(set_mek, row)
        mr += 1
    return mr

def imp_inv(zipfile: str, _sql: object, typ: int, ar: str): # -> tuple
    # zipfile - file to process
    # pdb - data base context manager
    # typ - invoice type
    # ar - 2 last digits of year
    # returns tuple of 1 if any arrors occured else records count and meta info

    global sn
    # 1 unpack file
    zipwd= Path(zipfile)
    zipdir= zipwd.parent
    file= zipwd.name
    print(zipdir, file)

    os.chdir(zipdir)
    _hm= ''
    with ZipFile(file) as zfile:
        for nz in zfile.namelist():
            if nz.startswith('HM') or nz.startswith('CM') or nz.startswith('DOM'):
                zfile.extract(nz)
                _hm= nz
                c= nz[0]
                if c in('H', 'D'):
                    _lm= nz.replace(c, 'L')
                else:
                    _lm= nz.replace(c, 'LC')
                zfile.extract(_lm)

    if len(_hm) == 0:
        #bad invoice file name
        return ((1, 0), False)

    # import PMUs with tarifs
    if typ == 6:
        return imp_usl(_hm, _sql)

    sn.qurs = _sql.qurs
    sn.inv_table = tmp_table_name()
    create= sql.SQL(config.CREATE_TBL_INV).format(sn.inv_table)
    sn.qurs.execute(create)
    sn.insert_inv = sql.SQL(config.INS_INV_TMP).format(sn.inv_table)
    sn.insert_pers = sql.SQL(config.PERSQ_TMP).format(sn.inv_table)

    #sn.qurs.execute(config.TRUNC_TBL_INV)
    #sql.db.commit()

    # 2. process files
    # ---------------------------------------------
    for (f, r) in ( (_hm, sn.zap), (_lm, sn.pers)):
        zp_xml(f, r)
        _sql._db.commit()

    mek= set_mek(ar)
    _sql._db.commit()
    count= sql.SQL(config.COUNT_INV_TMP).format(sn.inv_table)
    sn.qurs.execute(count)
    rc= sn.qurs.fetchone()

    #sn.qurs.close()

    os.remove(_hm)
    os.remove(_lm)
    setattr(_sql, 'inv_table', sn.inv_table)
    return ((rc[0], mek), True) if bool(rc) and len(rc) > 0 else ((2, 0), False)
