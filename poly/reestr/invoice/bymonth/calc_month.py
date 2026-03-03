

import os
import shutil
from typing import NamedTuple
from pathlib import Path
from datetime import date

#from psycopg2 import sql as psy_sql
#import psycopg2.extras
#from poly.reestr.invoice.impex import config as imp_conf
from poly.utils.files import get_name_tail
from poly.reestr.invoice.bymonth import config
from poly.reestr.invoice.impex.export_invoice import SqlExportInvoice

class CalcMonth(SqlExportInvoice):
    def __init__(self,
        flask_app: object, sql: object, mo_code: str, smo: int,
        month: str, year: str, typ: int, export_folder: str, is_calc='',
    ):
        """
        @param: is_calc='': here is the self MO short code
          used for substring in output file name
        """
        super().__init__(flask_app, sql, mo_code, smo,
            month, year, typ, export_folder, is_calc)

        self._year = int(year) % 100
        self._month = int(month)
        self.icode=''

    def check_tables_exists(self):
        return True

    def init_workbook(self):
        """ Init workbook once """
        if self.workbook is None:
            super().init_workbook()
        # return same workbook
        return self.workbook

    def prepare_sheet(self, sheet):
        sheet['B1'].value = self.period
        sheet['C1'].value = self.sheet_title
        # begin from 6th string
        return 6, 4

    def select_export_data(self):
        _data = config.GET_MONTH_USL.format(
            talons_table=f'talonz_clin_{self._year}',
            para_table=f'para_clin_{self._year}',
            month=self._month,
            icode=self.icode
        )
        self.qurs.execute(_data)
        return self.qurs.fetchall()

    def extract_data(self, row, cells_in_row):
        """ make the xlsx's row list for the MO invoice's reestr"""
        prop = lambda attr: getattr(row, attr, '')
        sprop = lambda attr: getattr(row, attr, '  ')
        _d = [ '' for _ in range(cells_in_row)]
        _d[0] = prop('mo_code')
        _d[1] = prop('mo_name')
        _d[2] = prop('ntal')
        _d[3] = float(prop('sum_usl'))
        return _d


