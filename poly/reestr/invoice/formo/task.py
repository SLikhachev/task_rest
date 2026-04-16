""" formo task API handlers """

from collections import namedtuple
from flask import current_app
from flask_restful import reqparse, inputs
from poly.utils.sqlbase import SqlProvider
from poly.task import RestTask
from poly.utils.fields import month_field
from poly.reestr.invoice.formo.calc_for_mo import ExportMoInvoce
from poly.reestr.invoice.formo import config
from poly.reestr.invoice.impex import config as imp_conf
from poly.reestr.invoice.bymonth import config as code_conf


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
                expo = ExportMoInvoce(
                    current_app, _sql, '999', '',
                    self.month, self.year, config.PACK_TYPE, cwd, '_calc',
                    args['fresh']
                )
                sent = args['sent']
                rmos = []
                recs = 0
                for mo_code, mo_name in expo.get_mos():
                    expo.mo_code = mo_code
                    expo.payer = mo_name
                    expo.calc = mo_code
                    _mo_recs = 0
                    # for CT, MRI select/export separately
                    for icode, inames in code_conf.ICODES.items():
                        expo.sheet_title = inames[1]
                        expo.icode = icode
                        _recs, _ = expo.export(
                            sheet_title=inames[1],
                            sent=sent,
                            close_workbook=False
                        )
                        _mo_recs += _recs
                    # close workbook after last icode iteration
                    _, file = expo.close_workbook(_mo_recs, close_workbook=True)
                    rmos.append({
                        'mo': mo_code,
                        'name': mo_name,
                        'recs': _mo_recs,
                        'file': file
                    })
                    recs += _mo_recs
                    #break
                #print(rmos)
            except Exception as e:
                raise e
                return self.abort(500, f'Ошибка формрования расчета {e}')
        # Context manager closed

        #print(rmos)
        zipfile = expo.make_zip(rmos)
        #zipfile = "zipfile"

        return self.resp(zipfile,
            f'Расчет {imp_conf.TYPE[config.PACK_TYPE-1][1]} Записей обработано {recs}', True)
