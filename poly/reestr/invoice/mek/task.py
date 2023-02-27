
import os
from datetime import datetime
from pathlib import Path
from flask import current_app, request
from flask_restful import reqparse
from poly.utils.sqlbase import SqlProvider
from poly.task import RestTask
from poly.utils.fields import month_field
from poly.utils.files import get_name_tail
from poly.reestr.invoice.mek import config
from poly.reestr.invoice.mek.move_mek import move_mek

parser = reqparse.RequestParser()
parser.add_argument('month', type=month_field, required=True,
    location=('form', 'values'), help='{From month date in YYYY-MM format required}')
parser.add_argument('target', type=month_field, required=True,
    location=('form', 'values'), help='{To month date in YYYY-MM format required}')


class MoveMek(RestTask):

    def __init__(self):
        super().__init__()
        self.mo_code = current_app.config['STUB_MO_CODE']

    def month_val(self, val):
        try:
            m = int(val)
        except:
            m = 1
        if m <= 0 or m > 12:
            return 1
        return m

    def month_str(self, month=0):
        m = month if bool(month) else self.from_month
        return  f'{current_app.config["MONTH"][m-1]} {self.from_year}'

    def parse_dates(self):
        args = parser.parse_args()
        print(args)
        self.from_year, self.from_month = args['month']
        self.to_year, self.to_month= args['target']
        self._year = self.from_year[2:]
        self.from_year = int(self.from_year)
        self.to_year = int(self.to_year)
        self.from_month= self.month_val(self.from_month)
        self.to_month = self.month_val(self.to_month)
        print(self.from_year, self.from_month, self.to_month)


    # move to next month task
    def post(self):

        try:
            self.parse_dates()
        except Exception as exc:
            raise exc
            #return self.abort(400, exc)

        if self.this_year != self.to_year:
            return self.abort(400, f'Переносить МЭК можно только в текущем году')
        if self.to_month <= self.from_month:
            return self.abort(400, f'Переносить МЭК можно только вперед')

        with SqlProvider(self) as _sql:
            try:
                rc= move_mek(_sql, self.this_year, self.from_month, self.to_month)
            except Exception as exc:
                raise exc
                return self.abort(500, f'Ошибка переноса МЭК {exc}')

        if not bool(rc):
            return self.resp('',
                f'Нет МЭКов за {self.month_str()}', False)

        return self.resp('',
            f'Пернесли МЭКи на {self.month_str(self.to_month)} записей {rc}.',
            True
        )

    # export to csv task
    def get(self):

        try:
            self.parse_dates()
        except Exception as exc:
            raise exc
            #return self.abort(400, exc))

        with SqlProvider(self) as _sql:
            ar= self.from_year-2000
            _sql.qurs.execute(config.COUNT_MEK, (ar, self.from_month))
            mc= _sql.qurs.fetchone()

            if (mc is None) or mc[0] == 0:
                #qurs.close()
                return self.resp('',
                    f'Нет записей с МЭК за месяц {self.month_str()}', True)

            mc= mc[0]
            cwd = self.catalog('', 'reestr', 'mek')
            df= str(datetime.now()).split(' ')[0]
            copy_to = config.COPY_TO % (ar, self.from_month)
            copy_to = f'{copy_to} {config.STDOUT} ({config.CSV_OPTS});'
            #print(f'\n{copy_to}\n')
            filename= f"MEK_{df}_{get_name_tail(4)}.csv"
            file = os.path.join(cwd, filename)
            try:
                with open(file, 'w', encoding='UTF8') as _file:
                    _sql.qurs.copy_expert(copy_to, _file)
                assert Path(file).exists(), 'Ошибка экспотра в CSV файл не сформирован'
            except Exception as exc:
                raise exc
                return self.abort(500, f'Ошибка формирования файла МЭК')
            else:
                return self.resp(file,  f"МЭК за месяц {self.month_str()}, записей в файле {mc}", True)
            finally:
                pass
                #qurs.close()