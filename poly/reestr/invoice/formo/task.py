
#from datetime import datetime
#from pathlib import Path
from collections import namedtuple
from flask import current_app
from flask_restful import reqparse, inputs
from poly.utils.sqlbase import SqlProvider
from poly.task import RestTask
from poly.utils.fields import month_field
from poly.reestr.invoice.formo.calc_for_mo import ExportMoInvoce
from poly.reestr.invoice.formo import config
from poly.reestr.invoice.impex import config as imp_conf

parser = reqparse.RequestParser()
parser.add_argument('month', type=month_field, required=True,
    location=('json', 'form'), help='{Date in YYYY-MM format required}')
#if SENT is flase dont setup talon_type=2 as sent talon
parser.add_argument('sent', type=inputs.boolean, default=False,
    location=('json', 'form'), help='{Sent flag}')
# if FRESH is false ignore already sent and accepted talons and produce full pack
parser.add_argument('fresh', type=inputs.boolean, default=False,
    location=('json', 'form'), help='{Fresh flag}')

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
                    self.month, self.year, config.PACK_TYPE, cwd, '_calc',
                    args['fresh']
                )
                sent = args['sent']
                rmos = []
                recs = 0
                for mo_code, mo_name in exporter.get_mos():
                    exporter.mo_code = mo_code
                    exporter.payer = mo_name
                    exporter.calc = mo_code
                    _recs, _reestr = exporter.export(sent=sent)
                    rmos.append({
                        'mo': mo_code,
                        'name': mo_name,
                        'recs': _recs,
                        'file': exporter.xlsout_abspath
                    })
                    recs += _recs
                    #break
                #print(rmos)
            except Exception as e:
                raise e
                return self.abort(500, f'Ошибка формрования расчета {e}')
        # Context

        zipfile = exporter.make_zip(rmos)

        return self.resp(zipfile,
            f'Расчет {imp_conf.TYPE[config.PACK_TYPE-1][1]} Записей обработано {recs}', True)
