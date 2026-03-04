

import os
import shutil
from typing import NamedTuple
from pathlib import Path
from datetime import date
from decimal import getcontext, Decimal
from poly.utils.files import get_name_tail
from poly.reestr.invoice.formo import config
from poly.reestr.invoice.impex.export_invoice import SqlExportInvoice

class ExportMoInvoce(SqlExportInvoice):
    def __init__(self,
        flask_app: object, sql: object, mo_code: str, smo: int,
        month: str, year: str, typ: int, export_folder: str, is_calc='',
        fresh: bool=False):
        """
        @param: is_calc='': here is the mo payer short code
          used for substring in output file name
        """
        super().__init__(flask_app, sql, mo_code, smo,
            month, year, typ, export_folder, is_calc)

        self._year = int(year) % 100
        self._month = int(month)
        self.fresh = fresh

    def get_mos(self):
        _data = config.GET_MOS.format(
            year=self._year, month=self._month
        )
        self.qurs.execute(_data)
        return self.qurs.fetchall()

    def check_tables_exists(self):
        return True

    def prepare_sheet(self, sheet):
        sheet['B2'].value = self.period
        sheet['E3'].value = self.payer
        self.total_sum_column=10
        # begin from 17th string
        return 9, 10

    def select_export_data(self):
        fresh = config.FRESH if self.fresh else config.ALLTYPES
        _data = config.GET_INV_ROW.format(
            year=self._year, month=self._month,
            mo_code=self.mo_code, fresh=fresh
        )
        self.qurs.execute(_data)
        return self.qurs.fetchall()

    def extract_data(self, row, cells_in_row):
        """ make the xlsx's row list for the MO invoice's reestr"""
        prop = lambda attr: getattr(row, attr, '')
        sprop = lambda attr: getattr(row, attr, '  ')
        fst = lambda attr: sprop(attr)[0].upper() if sprop(attr) else ''
        _d = [ '' for _ in range(cells_in_row)]
        _d[0] = prop('num')
        _d[1] = f"{sprop('fam')} {fst('im')}. {fst('ot')}."
        _d[2] = prop('pol')
        _d[3] = prop('dr')
        _d[4] = prop('polis')
        _d[5] = prop('napr')
        _d[6] = prop('ds')
        _d[7] = f"{prop('open_date')}~{prop('close_date')}"
        _d[8] = prop('code_usl')
        _d[9] = Decimal(prop('sum_usl'))
        self.total_sum += _d[9]
        return _d

    def set_sent(self, talon_row: NamedTuple):
        upadate = config.SET_SENT.format(
            year=self._year, tal_num=talon_row.num
        )
        self.qurs.execute(upadate)

    def make_zip(self, rmos: list):
        day=date(int(self.year), int(self.month), 1)
        zipname=f"{day.strftime('%b')}-{get_name_tail(5)}"
        tmpdir = Path(self.export_dir) / zipname
        tmpdir.mkdir(exist_ok=True)
        for mo in rmos:
            shutil.move(mo['file'], tmpdir)
        os.chdir(str(tmpdir))
        #print(self.xmldir, tmpdir, base_name)
        shutil.make_archive(str(tmpdir), 'zip', tmpdir)
        return f"{zipname}.zip"
