""" definition of the calss for export data to the XLSX file """

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
        Initialize the class for export data to the XLSX file

        @param: flask_app: object - current flask app object
        @param: sql: object - Sql provider context manager
        @param: mo_code: str - full MO_CODE i.e '250799'
        @param: smo: int, code of (0,  25011, 25016 )
        @param: month: str(2) - 01..12
        @param: year: str(4) - '2020'
        @param: typ: int, - 1-5 package type
        @param: export_folder: str, path to the folder where file will be stored
        @param: is_calc='': str - here is the mo payer short code
          used for substring in output file name
        @param: fresh: bool=False - if True, then only fresh records will be selected
        """
        super().__init__(flask_app, sql, mo_code, smo,
            month, year, typ, export_folder, is_calc)

        # save year and month in the object
        self._year = int(year) % 100
        self._month = int(month)

        self.fresh = fresh

    def get_mos(self) -> list:
        """
        Get all MOs for the given year and month from DB

        @return: list of tuples containing MO information
        """
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
        sheet['B2'].value = self.sheet_title
        self.total_sum_column=10
        # begin from 17th string
        return 9, 10

    def select_export_data(self):
        fresh = config.FRESH if self.fresh else config.ALLTYPES
        _data = config.GET_INV_ROW.format(
            year=self._year,
            month=self._month,
            mo_code=self.mo_code,
            icode=self.icode,
            fresh=fresh
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
        """
        Mark the talon as sent in the database

        @param: talon_row: NamedTuple - row from the talonz table
        """
        # update talon type to 2 (sent)
        upadate = config.SET_SENT.format(
            year=self._year, tal_num=talon_row.num
        )
        # execute update query
        self.qurs.execute(upadate)

    def make_zip(self, rmos: list) -> str:
        """
        Create a zip archive containing the MO invoices

        @param: rmos: list - list of MO invoices
        @return: str - name of the zip archive
        """
        day = date(int(self.year), int(self.month), 1)
        zipname = f"{day.strftime('%b')}-{get_name_tail(5)}"
        tmpdir = Path(self.export_dir) / zipname
        tmpdir.mkdir(exist_ok=True)

        os.chdir(str(self.export_dir))
        # Move all the MO invoices to the temporary directory
        for mo in rmos:
            shutil.move(mo['file'], tmpdir)

        # Change the current directory to the temporary directory
        os.chdir(str(tmpdir))

        # Create a zip archive from the temporary directory
        shutil.make_archive(str(tmpdir), 'zip', tmpdir)

        # Return the name of the zip archive
        return f"{zipname}.zip"
