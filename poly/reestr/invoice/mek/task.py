
import os
from datetime import datetime
from flask import current_app
from flask_restful import reqparse
from poly.utils.sqlbase import SqlProvider
from poly.reestr.task import RestTask
from poly.utils.fields import month_field
from poly.utils.files import get_name_tail
from poly.reestr.invoice.mek import config
from poly.reestr.invoice.mek.move_mek import move_mek

parser = reqparse.RequestParser()
parser.add_argument('month', type=month_field, required=True,
    location=('json', 'values'), help='{From month date in YYYY-MM format required}')
parser.add_argument('target', type=month_field, required=True,
    location=('json', 'values'), help='{To month date in YYYY-MM format required}')


class MoveMek(RestTask):

    def __init__(self):
        super().__init__()
        self.mo_code = current_app.config['STUB_MO_CODE']

    def exepn(self,e ):
        return f'{e.__class__.__name__}: {e}'

    def month_val(self, val):
        try:
            m = int(val)
        except:
            m = 1
        if m <= 0 or m > 12:
            return 1
        return m

    def month_str(self, month=0):
        m = month if bool(month) else self.month
        return  f'{current_app.config["MONTH"][m-1]} {self.year}'

    def dispatch_request(self, *args, **kwargs):
        try:
            vals = parser.parse_args()
            self.year, self.month = vals['month']
            _, self.target_month = vals['target']
            self.year = int(self.year)
            self.month= self.month_val(self.month)
            self.target_month = self.month_val(self.target_month)
        except Exception as e:
            return self.abort(400, self.exepn(e))
        return super().dispatch_request(*args, **kwargs)

    # move to next month task
    def post(self):

        if self.this_year != self.year:
            return self.abort(400, f'Переносить МЭК можно только в текущем году')
        if self.target_month <= self.month:
            return self.abort(400, f'Переносить МЭК можно только вперед')

        with SqlProvider(self.sql_srv, self.mo_code, self.year, self.month) as _sql:
            try:
                rc= move_mek(_sql, self.this_year, self.month, self.target_month)
            except Exception as e:
                raise e
                return self.abort(500, f'Ошибка переноса МЭК {e}')

        if not bool(rc):
            return self.resp('',
                f'Нет МЭКов за {self.month_str()}', False)

        return self.resp('',
            f'Пернесли МЭКи на {self.month_str(self.target_month)} записей {rc}.',
            True)

    # export to csv task
    def get(self):

        with SqlProvider(self.sql_srv, self.mo_code, self.year, self.month) as _sql:
            ar= self.year-2000
            _sql.qurs.execute(config.COUNT_MEK, (ar, self.month))
            mc= _sql.qurs.fetchone()

            if (mc is None) or mc[0] == 0:
                #qurs.close()
                return self.resp('',
                    f'Нет записей с МЭК за месяц {self.month_str()}', True)

            mc= mc[0]
            cwd = self.catalog('', 'reestr', 'mek')
            df= str(datetime.now()).split(' ')[0]
            filename= f"MEK_{df}_{get_name_tail(4)}.csv"
            file = os.path.join(cwd, filename)

            _q= config.MEK_FILE % file
            # actually
            _q = f'{config.TO_CSV}{_q}'
            try:
                _sql.qurs.execute(_q, (ar, self.month))
            except Exception as e:
                raise e
                return self.abort(500, f'Ошибка формирования файла МЭК')
            else:
                return self.resp(file,  f"МЭК за месяц {self.month_str()}, записей в файле {mc}", True)
            finally:
                pass
                #qurs.close()