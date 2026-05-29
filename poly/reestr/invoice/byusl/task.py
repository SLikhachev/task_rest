""" by usl task API handlers """

from datetime import date
from collections import namedtuple
from flask import current_app
from flask_restful import reqparse, inputs
from poly.utils.sqlbase import SqlProvider
from poly.utils.fields import month_field
from poly.task import RestTask
from poly.reestr.invoice.byusl.calc_usl import CalcUsl
from poly.reestr.invoice.byusl import config
from poly.reestr.invoice.impex import config as imp_conf


class CalcByuslException(Exception):
    pass

parser = reqparse.RequestParser()
##parser.add_argument('year', type=inputs.int_range(2020, 2030), required=True,
#    location=('json', 'form'), help='{Year in YYYY format required}')
# select in month
parser.add_argument('month', type=month_field, default=('2012', '01'),
    location=('json', 'form'), help='{Date in YYYY-MM format}')
# select from date -- to date
parser.add_argument('date_beg', type=inputs.date, default=None,
    location=('json', 'form'), help='{Date in YYYY-MM-DD format}')
parser.add_argument('date_end', type=inputs.date, default=None,
    location=('json', 'form'), help='{Date in YYYY-MM-DD format}')
parser.add_argument('talons_mo', type=int, default=0, # all MOs
    location=('json', 'form'), help='{Talons MO naprav code Integer}')
#Claculate only closed
parser.add_argument('closed', type=inputs.boolean, default=False,
    location=('json', 'form'), help='{Calc only closed}')
#Claculate full year
parser.add_argument('onyear', type=inputs.boolean, default=False,
    location=('json', 'form'), help='{Calc on the full year}')

class CalcByusl(RestTask):

    def __init__(self):
        super().__init__()

    def post(self):
        try:
            args = parser.parse_args()
            #print(f'CalcbyUsl args: {args}')
            self.year, self.month = args['month']
            self.date_beg = args['date_beg']
            self.date_end = args['date_end']
            self.npr_mo = args['talons_mo']
            self.closed = args['closed']
            self.onyear = args['onyear']
        except Exception as e:
            raise e
            #return self.abort(400, f'CalcByUsl args parser: {e}')
        _calc = '_month_calc'
        # if date_beg and date_end set then ignore form month field value
        if self.date_beg and self.date_end:
            self.year = str(self.date_beg.year)
            self.month = '0'
            _calc = '_period_calc'
        cwd = self.catalog('', 'reestr', 'formo')
        self.mo_code = current_app.config['STUB_MO_CODE']
        self._year = self.year[2:]
        if self.onyear:
            _calc = '_year_calc'

        with SqlProvider(self) as _sql:
            try:
                calc = CalcUsl(
                    current_app, _sql, '796', self.npr_mo,
                    self.month, str(self.year),
                    self.date_beg, self.date_end,
                    config.PACK_TYPE, cwd, _calc,
                    self.closed, self.onyear
                )
                _table = calc.test_tables_exists()
                if len(_table) > 0:
                    #print(f'before rise CalcYearException: {_table}')
                    raise CalcByuslException(f'Таблица {_table} не найдена')

                recs=0
                for icode, inames in config.ICODES.items():
                    calc.sheet_title = inames[1]
                    calc.icode= icode
                    _recs, file = calc.export(
                        sheet_title=inames[1],
                        sent=False,
                        close_workbook=False
                    )
                    if _recs < 0:
                        raise CalcByuslException(f'Ошибка формирования расчета {file}')
                    recs += _recs
                _, file = calc.close_workbook(recs, close_workbook=True)
            except CalcByuslException as e:
                #_sql.close()
                return self.abort(400, f'{e}')
            except Exception as e:
                raise e
                return self.abort(500, f'Ошибка формрования расчета {e}')

        return self.resp(file,
            f'Расчет {imp_conf.TYPE[config.PACK_TYPE-1][1]} Записей обработано {recs}', True)
