""" definition of the calss for export data to the XLSX file """

import os
from typing import NamedTuple
from datetime import date
from pathlib import Path
import psycopg2.extras
from psycopg2 import sql as psy_sql
from flask import g
from openpyxl import load_workbook
from openpyxl.styles import Border, Side, colors
from poly.utils.files import get_name_tail
from poly.reestr.invoice.impex import config


class SqlExport:
    """ base class for export """

    def __init__(self,
        flask_app: object, sql: object, mo_code: str, smo: int,
        month: str, year: str, typ: int, export_folder: str, is_calc=''):
        """
           @param: flask_app: object - current flask app object
           @param: sql: object - Sql provider context manager
           @param: mo_code: str - full MO_CODE i.e '250799'
           @param: smo: int, code of (0,  25011, 25016 )
           @param: month: str(2) - 01..12
           @param: year: str(4) - '2020'
           @param: typ: int, - 1-5 package type
           @param: export_folder: str, path to the folder where file will be stored
           @param: is_calc='': str - if not empty then self calculated reestr
        """
        self.app = flask_app
        self.sql = sql

        # clean same values
        assert hasattr(sql, 'qurs'), "SqlExport: Нет связи с БД"

        self.qurs = sql.qurs
        self.mo_code = mo_code
        self.smo = smo
        self.month = month
        self.year = year
        self.typ = typ
        self.export_dir = export_folder
        self.calc = is_calc


    def check_table_name(self, name):
        assert hasattr(self.sql, name), f"Экспорт реестра: имя таблицы: {name} БД не определено"


    def get_mo_smo_name(self):
        """ select and return (SMO, MO) names from DB """
        _code= self.mo_code[-3:] # last 3 digits i.e short code
        self.qurs.execute(config.GET_MO_NAME, ( _code, ) )
        _mo= self.qurs.fetchone()
        if _mo:
            mo_name= _mo[0]
        else:
            mo_name= config.STUB_MO
        if self.smo > 0:
            #ins= 25000 + int(smo)
            self.qurs.execute(config.GET_SMO_NAME, ( self.smo, ))
            smo= self.qurs.fetchone()
            if smo:
                smo_name=  smo[0]
            else:
                smo_name= config.STUB_SMO
        else:
            smo_name= ''

        return mo_name, smo_name

    def border(self):
        return Border(
            left=Side(border_style='thin', color=colors.BLACK),
            right=Side(border_style='thin', color=colors.BLACK),
            top=Side(border_style='thin', color=colors.BLACK),
            bottom=Side(border_style='thin', color=colors.BLACK)
        )


    def init_workbook(self):

        self._tpl_name = config.TYPE[self.typ-1][2]
        self.tpl_name = f'{self._tpl_name}.xlsx'
        self.tpl_abspath = os.path.join(self.export_dir, 'tpl', self.tpl_name)

        if not os.path.exists(self.tpl_abspath):
            raise AttributeError(f"Шаблон {self.tpl_abspath} не найден")

        self.xlsout_fname = \
            f'{self._tpl_name}{self.calc}_{self.smo}_{self.month}_{self.year}_{get_name_tail(5)}.xlsx'
        self.xlsout_abspath = os.path.join(self.export_dir, self.xlsout_fname)

        self.period = f"За {self.app.config['MONTH'][int(self.month)-1]} {self.year} года"

        self.workbook = load_workbook(filename = self.tpl_abspath)
        self.workbook.active

        return self.workbook["Лист1"]


    def close(self, rows):
        self.workbook.save(self.xlsout_abspath)
        self.workbook.close()
        return rows, self.xlsout_fname


class SqlExportInvoice(SqlExport):
    """ export invoice DB table to xlsx file """

    def __init__(self,
        flask_app: object, sql: object, mo_code: str, smo: int,
        month: str, year: str, typ: int, export_folder: str, is_calc=''):

        super().__init__(flask_app, sql, mo_code, smo,
            month, year, typ, export_folder, is_calc)

        self.check_table_name('inv_table')


    def extract_for_smo(self, row: NamedTuple) -> list:
        """ make the xlsx's row list for the SMO invoice's reestr"""
        prop = lambda attr: getattr(row, attr, '')
        sprop = lambda attr: getattr(row, attr, '  ')
        fst = lambda attr: sprop(attr)[0].upper() if sprop(attr) else ''
        _d = [ '' for _ in range(20)]
        _d[0] = prop('nhistory')
        _d[1] = f"{sprop('fam')} {fst('im')}. {fst('ot')}."
        _d[2] = prop('w')
        _d[3] = prop('dr')
        #d[4] = ''
        #docser = row.docser or ' '
        #docnum = row.docnum or ' '
        #d[5] = '%s %s' % (docser, docnum)
        #d[6], d[7], d[8] = '', '', ''
        _d[9] = f"{prop('spolis')} {prop('npolis')} {prop('enp')}"
        #''.join(i for i in row.p_num if i.isdigit())
        # re.sub("\D", "", )
        _d[10] = prop('vidpom')
        _d[11] = prop('ds1')
        _d[12] = f"{prop('date_z_1')}~{prop('date_z_2')}"
        _d[13] = 1
        _d[14] = prop('profi')
        _d[15] = prop('prvs')
        _d[16] = price = prop('sumv')
        #d[17] = row.foms_price
        if prop('sump') == 0.00:
            #price -= row.sank_it
            if price:
                _d[5]= 'МЭК'
            else:
                _d[5]= 'ХЭК'
            price= 0.00
        _d[17] = price

        _d[18] = prop('rslt')
        #d[19] = row.ishod

        return _d


    def extarct_for_foms(self, smo_row: list, record_num: int):
        """ make xlsx's row list for TFOMS invoice's reestr"""
        # smo_row - list from extract_for_smo
        _d = ['' for _ in range(20)]

        _d[0] = record_num

        # idcase, fio
        _d[1], _d[2] = smo_row[0], smo_row[1]

        # pol
        _d[3]= smo_row[2]

        # date_birth, place_birth
        _d[4], _d[5] = smo_row[3], smo_row[4]

        # d[6] # document
        # d[7] # snils

        # polis
        _d[8] = smo_row[9]

        # vid_pom
        _d[9] = smo_row[10]

        # DS
        _d[10] = smo_row[11]

        # date
        _d[11], _d[12] = smo_row[12].split("~")

        idx = 13
        for _v in smo_row[13:]:
            _d[ idx ] = _v
            idx += 1

        return _d


    def check_tables_exists(self):
        """ check DB tables for export exists"""

        if len(self.calc) == 0:
            _data = psy_sql.SQL(config.COUNT_INV_TMP).format(self.sql.inv_table)
        else:
            _data= config.COUNT_MO
        self.qurs.execute(_data)
        return True if self.qurs.fetchone() else False


    def select_export_data(self):
        """ select all from DB """

        if len(self.calc) == 0:
            #_data = config.GET_ROW_INV
            _data = psy_sql.SQL(config.GET_ROW_INV_TMP).format(self.sql.inv_table)
        else:
            _data= config.GET_ROW_MO
        self.qurs.execute(_data)
        return self.qurs.fetchall()


    def export(self) -> tuple:
        """ main func """

        if not self.check_tables_exists():
            return (-1, "Нет экспотрной таблицы БД")

        mo_name, smo_name = self.get_mo_smo_name()

        sheet = self.init_workbook()

        if self.smo == 0:
            # ======= code for TFOMS =========
            sheet['C4'].value = self.period
            # begin from 17 string
            current_row = 17
        else:
            # ======= code for SMO ==========
            # local config has MOS dict with mo_code as KEY and tuple(OGRN, ) as value
            sheet['E2'].value = f"{mo_name} ОГРН {self.app.config['MOS'][self.mo_code][0]}"
            sheet['E7'].value = smo_name
            sheet['J1'].value = self.period
            # begin from 13 string
            current_row = 13

        border = self.border()

        rc_total = 1
        cells_in_row=20 # 20 cells in row

        for row in self.select_export_data():

            try:
                data = self.extract_for_smo(row)
            except Exception as _ex:
                print(_ex)
                print(row)
                raise _ex

            if self.smo == 0:
                data = self.extarct_for_foms(data, rc_total)

            for xrow in range(current_row, current_row+1):
                for xcol in range(1, cells_in_row):
                    try:
                        cell = sheet.cell(column=xcol, row=xrow, value= data[ xcol-1 ])
                        cell.border = border
                    except Exception as exc:
                        self.app.logger.debug(f"\n row {rc_total} {exc}")
                        self.app.logger.debug(data)
                        raise exc
                current_row += 1
                rc_total += 1

        return self.close(rc_total-1)
