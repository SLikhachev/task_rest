
#from datetime import datetime
#from pathlib import Path
from flask import current_app
from flask_restful import reqparse
from poly.utils.sqlbase import SqlProvider
from poly.reestr.task import RestTask
from poly.utils.fields import month_field
from poly.reestr.invoice.calc.calc_inv import calc_inv
#from poly.reestr.invoice.calc.calc_pmu import calc_pmu
from poly.reestr.invoice.impex.exp_inv import exp_inv
from poly.reestr.invoice.impex import config


parser = reqparse.RequestParser()
parser.add_argument('pack', type=int,
    default=1, location='form',
    help="{Тип фала счета: 1-АПП 2-Онкология ...}")
parser.add_argument('smo', type=int, default=0)
parser.add_argument('month', type=month_field, required=True,
    location=('json', 'form'), help='{Date in YYYY-MM format required}')

class InvCalc(RestTask):

    def __init__(self):
        super().__init__()

    def post(self):
        try:
            args = parser.parse_args()
            pack_type = args['pack']
            year, month = args['month']
        except Exception as e:
            return self.abort(400, f'{e}')

        mo_code = current_app.config['STUB_MO_CODE']
        wc= 0
        cwd = self.catalog('', 'reestr', 'calc')
        with SqlProvider(self.sql_srv) as db:
            try:
                # PMU
                if self.pack_type == 6:
                    return self.resp('', 'Расчет услуг не реализован', True)

                rc, res = calc_inv(
                    current_app,  db, args['smo'], month, year, pack_type)
                if  not res:
                    return self.abort(400, config.FAIL[rc])
                wc, xreestr = exp_inv(
                    current_app, db, mo_code,
                    args['smo'], month, year, pack_type, cwd, '_calc')

            except Exception as e:
                raise e
                return self.abort(500, f'Ошибка формрования расчета {e}')
        # Context

        return self.resp(xreestr,
            f'Расчет {config.TYPE[pack_type-1][1]} Записей обработано {wc}', True)
