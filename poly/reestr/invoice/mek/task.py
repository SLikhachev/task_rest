
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
    location=('json', 'form'), help='{From month: Date in YYYY-MM format required}')
parser.add_argument('target', type=month_field, required=True,
    location=('json', 'form'), help='{To month: Date in YYYY-MM format required}')


class MoveMek(RestTask):

    def __init__(self):
        super().__init__()

    def month_str(self, month='', year=''):
        try:
            m = int(month)
        except:
            m = int(self.month)
        y = self.year if len(year) == 0 else year
        return  f'{current_app.config["MONTH"][m-1]} {y}'

    def dispatch_request(self, *args, **kwargs):
        try:
            args = parser.parse_args()
            self.year, self.month = args['month']
            _, self.target_month = args['target']
        except Exception as e:
            return self.abort(400, f'{e}')
        return super().dispatch_request(*args, **kwargs)

    # move to next month task
    def post(self):

        if self.this_year != self.year:
            return self.abort(400, f'Переносить МЭК можно только в текущем году')
        if self.target_month <= self.month:
            return self.abort(400, f'Переносить МЭК можно только на вперед')

        with SqlProvider(self.sql_srv) as db:
            try:
                rc= move_mek(db, self.this_year, self.month, self.target_month)
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

        with SqlProvider(self.sql_srv) as db:
            qurs= db.cursor()
            ar= self.year[2:]
            qurs.execute(config.COUNT_MEK, (ar, self.month ))
            mc= qurs.fetchone()

            if (mc is None) or mc[0] == 0:
                qurs.close()
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
                qurs.execute(_q, (ar, self.month))
            except Exception as e:
                raise e
                return self.abort(500, f'Ошибка формирования файла МЭК')
            else:
                return self.resp(file,  f"МЭК за месяц {self.month_str()}, записей в файле {mc}", True)
            finally:
                qurs.close()