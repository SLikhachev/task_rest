""" by month task API handlers """

from collections import namedtuple
from flask import current_app
from flask_restful import reqparse, inputs
from poly.utils.sqlbase import SqlProvider
from poly.task import RestTask
from poly.utils.fields import month_field
from poly.reestr.invoice.bymonth.calc_month import CalcMonth
from poly.reestr.invoice.bymonth import config
from poly.reestr.invoice.impex import config as imp_conf

parser = reqparse.RequestParser()
parser.add_argument('month', type=month_field, required=True,
    location=('json', 'form'), help='{Date in YYYY-MM format required}')

class CalcBymonth(RestTask):

    """
    CalcBymonth class is used to generate in month report
    """
    def __init__(self):
        """
        Initialize the CalcBymonth class

        This class is used to generate by month report
        """
        super().__init__()

    def post(self):
        try:
            args = parser.parse_args()
            self.year, self.month = args['month']
        except Exception as e:
            return self.abort(400, f'CalcByMonth args parser: {e}')

        cwd = self.catalog('', 'reestr', 'formo')
        self.mo_code = current_app.config['STUB_MO_CODE']
        self._year = self.year[2:]

        with SqlProvider(self) as _sql:
            try:
                calc = CalcMonth(
                    current_app, _sql, '796', '',
                    self.month, self.year, config.PACK_TYPE, cwd, '',
                )
                recs=0
                for icode, inames in config.ICODES.items():
                    calc.sheet_title = inames[1]
                    calc.icode= icode
                    _recs, file = calc.export(
                        sheet_title=inames[1],
                        sent=False,
                        close_workbook=False
                    )
                    recs += _recs
                _, file = calc.close_workbook(recs, close_workbook=True)
            except Exception as e:
                raise e
                return self.abort(500, f'Ошибка формрования расчета {e}')

        return self.resp(file,
            f'Расчет {imp_conf.TYPE[config.PACK_TYPE-1][1]} Записей обработано {recs}', True)
