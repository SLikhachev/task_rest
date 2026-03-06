
from datetime import datetime
from decimal import getcontext, Decimal
from poly.reestr.invoice.byusl import config
from poly.reestr.invoice.impex.export_invoice import SqlExportInvoice

class CalcUsl(SqlExportInvoice):
    def __init__(self,
        flask_app: object, sql: object, mo_code: str, smo: int,
        month: str, year: str, typ: int, export_folder: str, is_calc='',
        closed: bool=False, onyear: bool=False
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
        self.tables=config.YEAR_TABLES.copy()
        self.closed = closed
        self.onyear = onyear

    def check_tables_exists(self):
        return True

    def test_tables_exists(self):
        _year = datetime.now().year % 100
        tarifs=''
        if self._year != _year:
            tarifs=f'_{self._year}'
        # prepare tables names
        for tbl, name in self.tables.items():
            self.tables[tbl]=name.format(year=self._year, tarifs=tarifs)
            self.qurs.execute(
                config.TEST_TABLE_EXISTS.format(self.tables[tbl])
            )
            res = self.qurs.fetchone()
            if not res.exists:
                return self.tables[tbl]


        return ''

    def init_workbook(self):
        """ Init workbook once """
        if self.workbook is None:
            super().init_workbook()
        # return same workbook
        return self.workbook

    def prepare_sheet(self, sheet):
        sheet['B1'].value = self.period
        sheet['C1'].value = self.sheet_title
        self.total_sum_column=5
        # begin from 6th string (row)
        return 6, 5

    def select_export_data(self):
        self.tables['icode'] = self.icode

        by_month = ''
        if not self.onyear:
            by_month=config.BY_MONTH.format(month=self._month)
        self.tables['by_month'] = by_month

        talon_type='>0'
        if self.closed:
            talon_type='=2'
        self.tables['talon_type'] = talon_type

        print(self.tables)
        _data = config.GET_YEAR_USL.format(
            **self.tables
        )
        self.qurs.execute(_data)
        return self.qurs.fetchall()

    def extract_data(self, row, cells_in_row):
        """ make the xlsx's row list for the MO invoice's reestr"""
        prop = lambda attr: getattr(row, attr, '')
        _d = [ '' for _ in range(cells_in_row)]
        _d[0] = prop('code_usl')
        _d[1] = prop('name')
        _d[2] = Decimal(prop('tarif')) if prop('tarif') else ''
        _d[3] = prop('kolvo_usl')
        _d[4] = Decimal(prop('summa_usl')) if prop('summa_usl') else ''
        if type(_d[4]) == Decimal:
            self.total_sum += _d[4]
        return _d


