
#from datetime import datetime
#from pathlib import Path
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
parser.add_argument('month', type=month_field, required=True,
    location=('json', 'form'), help='{Date in YYYY-MM format required}')
#Claculate full year
parser.add_argument('closed', type=inputs.boolean, default=False,
    location=('json', 'form'), help='{Calc only closed}')
#Claculate full year
parser.add_argument('onyear', type=inputs.boolean, default=False,
    location=('json', 'form'), help='{Calc on the year}')

class CalcByusl(RestTask):

    def __init__(self):
        super().__init__()

    def post(self):
        try:
            args = parser.parse_args()
            self.year, self.month = args['month']
            self.closed = args['closed']
            self.onyear = args['onyear']
            #print(f'CalcOnYear args: {args}')
        except Exception as e:
            return self.abort(400, f'CalcOnYear args parser: {e}')

        cwd = self.catalog('', 'reestr', 'formo')
        self.mo_code = current_app.config['STUB_MO_CODE']
        self._year = self.year[2:]

        with SqlProvider(self) as _sql:
            try:
                calc = CalcUsl(
                    current_app, _sql, '796', '',
                    self.month, str(self.year), config.PACK_TYPE, cwd, '',
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
