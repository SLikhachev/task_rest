""" The paraclinic services file geberator """

from psycopg2 import sql as psy_sql
from poly.reestr.invoice.impex import config
from .export_invoice import SqlExport


class SqlExportPmus(SqlExport):
    """ export pmus DB table to xlsx file """

    def __init__(self,
        flask_app: object, sql: object, mo_code: str, smo: int,
        month: str, year: str, typ: int, export_folder: str, is_calc=''):

        super().__init__(flask_app, sql, mo_code, smo,
            month, year, typ, export_folder, is_calc)

        self.check_table_name('usl_table')


    def check_tables_exists(self):
        """ check DB tables for export exists"""

        if len(self.calc) == 0:
            _data = psy_sql.SQL(config.COUNT_USL_TMP).format(self.sql.usl_table)
        else:
            # self calc do not implemented
            return False
        self.qurs.execute(_data)
        return True if self.qurs.fetchone() else False


    def select_export_data(self):
        """ select all from DB """
        self.qurs.execute(psy_sql.SQL(config.GET_USL_TMP).format(self.sql.usl_table))
        return self.qurs.fetchall()


    def export(self):
        """ main func """
        if not self.check_tables_exists():
            return (-1, "Нет экспотрной таблицы БД")

        self.typ=6 # pmu

        _, smo_name = self.get_mo_smo_name()

        sheet = self.init_workbook()
        rc_total = 1
        current_row=21
        cells_in_row=range(1, 6)

        sheet['B15'].value = f"{self.period}    {smo_name}"

        for row in self.select_export_data():

            data = ( row.code_usl, row.name,  row.tarif, row.kol_usl, row.kol_usl*row.tarif)
            for xrow in range(current_row, current_row+1):
                for xcol in cells_in_row:
                    cell = sheet.cell(column=xcol, row=xrow, value= data[ xcol-1 ])
                    cell.border = self.border()
            current_row += 1
            rc_total += 1

        _crow = current_row-1
        for xcol in cells_in_row:
            val=''
            if xcol == 1:
                val="ИТОГО"
            if xcol == 4:
                val=f'=SUM(D21:D{_crow})'
            if xcol==5:
                val=f'=SUM(E21:E{_crow})'
            cell = sheet.cell(column=xcol, row=current_row, value= val)
            cell.border = self.border()

        sheet.cell(column=2, row=current_row+4, value= "Генеральный директор")
        sheet.cell(column=3, row=current_row+4, value= "ДЕНИСОВА С. А.")
        sheet.cell(column=2, row=current_row+6, value= "Исполнитель   202-51-45   Чамбайшин Ю.А.")

        return self.close(rc_total)
