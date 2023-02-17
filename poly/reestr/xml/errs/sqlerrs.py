""" errors file process class definitions """

from typing import List, Tuple, NamedTuple
from collections import namedtuple
#import psycopg2
#import psycopg2.extras
import xml.etree.cElementTree as ET
from poly.utils.sqlbase import SqlProvider
from poly.reestr.xml.errs import config

Talon = namedtuple('Talon',
    ['tal_num', 'open_date', 'close_date', 'crd_num', 'fam']
)

class XmlErrors:
    """ Struct of parsed file
    <?xml version="1.0" encoding="utf-8" ?>
    - <FLK_P>
          <FNAME>VM250228T25_19072285.xml</FNAME>
          <FNAME_I>HM250228T25_19072285.xml</FNAME_I>
    - <SCHET>
        <CODE>2281908</CODE>
        <CODE_MO>250228</CODE_MO>
        <YEAR>2019</YEAR>
        <MONTH>7</MONTH>
        <NSCHET>228190801</NSCHET>
        <DSCHET>2019-07-31</DSCHET>
      </SCHET>
    - <ZAP>
        <N_ZAP>55665</N_ZAP>
        - <SL>
            <SL_ID>1</SL_ID>
            <IDCASE>55665</IDCASE>
            <NHISTORY>55665</NHISTORY>
            <CARD />
            <SMO>25016</SMO>
            <SMO_FOND>25016</SMO_FOND>
            - <OTKAZ>
                <I_TYPE>910</I_TYPE>
                <COMMENT>-1 - Нет информации о страхованиях в ЦС ЕРЗ ОМС!</COMMENT>
                </OTKAZ>
            - <OTKAZ>
                <I_TYPE>910</I_TYPE>
                <COMMENT />
                </OTKAZ>
            - <OTKAZ>
                <I_TYPE>903</I_TYPE>
                <COMMENT />
            </OTKAZ>
        </SL>
    </ZAP>

    errors_table struct:
        tal_num int,
        open_date date,
        close_date date,
        crd_num varchar(20),
        fam varchar(40),
        error int,
        cmt text,
        cuser name

    """

    def __init__(self,
        config: object,
        err_file: str,
        mo_code: str, _year: str, month: str,
        ignore: tuple, errors_action='ignore'):
        """
        @param: config: object of the DB config
        @param: error_file: string (full path) name of the errors' xml file saved
        @param: mo_code: str(6) code of MO
        @param: _year: str(2)
        @param: month: str(2)
        @param: ignore: tuple('824', ) tuple of str as errors code to ignore during process
        @param: errors: str if
            == 'ignore', then ignore tuple will be used in process
            == 'select' then only errors with codes in ignore will be selected
    """

        self.sql = config
        self.err_file = err_file
        self.mo_code = mo_code
        self._year = _year
        self.month = month
        self.ignore = ignore
        self.err_action = errors_action
        self.errors_set= set()

        # select talon DB query
        self.select_talon = None

        self.mark_talon= None

        self.qurs= None
        print(f'\n --- ERR_FILE: {self.err_file}\n')


    def process_zap(self, zap) -> List[Tuple]:
        """ process current xml tree starts with 'ZAP' tag
            @param: zap: root tree's node
            @param: ignore: tuple('824', ) ignored or selected errors' codes
            @param: errors: str if
                == 'ignore', then errors with codes in ignore will be ignored
                == 'select' then only errors with codes in ignore will be selected

            return list( (idcase, card, error_code, comment), )
            where idcase = tal_num, card=crd_num
        """
        was_found= []
        res= []
        sl_tag = zap.find('SL')
        card = sl_tag.find('CARD').text
        idcase = int( sl_tag.find('IDCASE').text)

        for otkaz_tag in sl_tag.findall('OTKAZ'):
            err = otkaz_tag.find('I_TYPE').text # was int
            if self.err_action == 'ignore' and err in self.ignore:
                continue
            if self.err_action == 'select' and err not in self.ignore:
                continue
            if err in was_found:
                continue
            was_found.append(err)
            comment= otkaz_tag.find('COMMENT').text
            res.append( ( idcase, card, err, comment ) )

        return res # list of tuples


    def get_talon(self, tal_num: str) -> NamedTuple:
        """ select talon record from talonz DB table
            return psycopg2 NamedTuple or None if record not found
        """
        self.qurs.execute(self.select_talon, (tal_num,))
        return self.qurs.fetchone()


    def write_error(self, res: list, cuser: str) -> NamedTuple:
        """ write error record in DB errors_table
            @param: res: list( (idcase, card, error_code, comment), )
            @param: cuser: str name of the current cuser DB param

            return talon DB record or custom
        """

        # we get the 1st tuple in the list (all errors belong to same talon)
        talon = self.get_talon(res[0][0])
        if talon is None: # no such record in table
            # make empty talon
            talon= Talon(res[0][0], None, None, '', 'Талон не найден')
        else:
            self.errors_set.add( int(talon.tal_num) )
        for err in res:
            error_code = err[2]
            self.qurs.execute ( config.GET_ERROR_NAME, (error_code, ) )
            error_desc= self.qurs.fetchone()
            desc= 'Нет описания'
            if error_desc:
                desc= error_desc[0]

            self.qurs.execute( config.WRITE_ERROR,
                (talon.tal_num, talon.open_date, talon.close_date, talon.crd_num, talon.fam,
                error_code, str(desc), cuser )
            )
        return talon


    def mark_talons(self):
        """ update talonz table records, set its 'type' as don't sent yet (=1)
            so these records will be added to xml pack next time
        """
        for talon in self.errors_set: # set() of
            self.qurs.execute(self.mark_talon, (talon,))
        # reset set
        self.errors_set.clear()


    def process_errors_file(self):
        """
            return int of records (errors) written in DB error_table
        """

        with SqlProvider(self) as _sql:

            # clean errors_table manually
            _sql.truncate_errors()
            self.qurs = _sql.qurs
            # select talon DB query
            self.select_talon= config.GET_TALON % ( _sql.talon_tbl, 'cardz_clin') + config.TAL
            # update talon DB query
            self.mark_talon= config.MARK_TALON % _sql.talon_tbl + '%s;'

            context = ET.iterparse(self.err_file, events=("start", "end"))
            event, root = next(context)
            root.clear()
            cnt = 0
            for event, elem in context:
                if event == "end" and elem.tag == "ZAP":
                    root = elem
                    # process current tree
                    res = self.process_zap(root)
                    if len(res) > 0:
                        _ = self.write_error(res, _sql.cuser)
                        cnt += 1
                    root.clear()

            self.mark_talons()

            _sql._db.commit()
            _sql.qurs.close()

        return cnt

