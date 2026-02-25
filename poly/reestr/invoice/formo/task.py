
#from datetime import datetime
#from pathlib import Path
from collections import namedtuple
from flask import current_app
from flask_restful import reqparse
from poly.utils.sqlbase import SqlProvider
from poly.task import RestTask
from poly.utils.fields import month_field
from poly.reestr.invoice.formo.calc_for_mo import ExportMoInvoce
from poly.reestr.invoice.formo import config
from poly.reestr.invoice.impex import config as imp_conf

parser = reqparse.RequestParser()
parser.add_argument('month', type=month_field, required=True,
    location=('json', 'form'), help='{Date in YYYY-MM format required}')

class CalcFormo(RestTask):

    def __init__(self):
        super().__init__()

    def post(self):
        try:
            args = parser.parse_args()
            self.year, self.month = args['month']
        except Exception as e:
            return self.abort(400, f'MoCalc args parser: {e}')
        cwd = self.catalog('', 'reestr', 'formo')
        self.mo_code = current_app.config['STUB_MO_CODE']
        self._year = self.year[2:]

        with SqlProvider(self) as _sql:
            try:
                exporter = ExportMoInvoce(
                    current_app, _sql, '999', '',
                    self.month, self.year, config.PACK_TYPE, cwd, '_calc'
                )
                rmos = []
                recs = 0
                for mo in exporter.get_mos():
                    exporter.mo_code = mo[0]
                    exporter.payer = mo[1]
                    exporter.calc = mo[0]

                    _recs, _reestr = exporter.export()
                    rmos.append({
                        'mo': mo[0],
                        'name': mo[1],
                        'recs': _recs,
                        'reestr': _reestr
                    })
                    recs += _recs
                    #break
                print(rmos)
            except Exception as e:
                raise e
                return self.abort(500, f'Ошибка формрования расчета {e}')
        # Context

        return self.resp(_reestr,
            f'Расчет {imp_conf.TYPE[config.PACK_TYPE][1]} Записей обработано {recs}', True)
