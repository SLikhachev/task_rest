
#import os
from datetime import date
from flask import request, current_app
from flask_restful import reqparse
from poly.task import RestTask
from poly.utils.sqlbase import SqlProvider

COUNT_TFOMS = 'SELECT COUNT(*) FROM tfoms';

# def requests args
parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('param', help='Тестовая задача')


class TestTask(RestTask):

    def __init__(self):
        super().__init__()
        self.mo_code = current_app.config['STUB_MO_CODE']
        self.date = date.today().isoformat()
        self._date = self.date.split('-')
        self.year = self._date[0]
        self._year = self.year[2:]
        self.year = int(self.year)
        self.month= self._date[1]


    def get(self):
        try:
            args = parser.parse_args()
        except Exception as exc:
            return self.abort(400, f'Неверный запрос: {exc}')

        param = args['param']
        return {
            'task': self.task,
            'rdbm': self.rdbm
        }.get( param, self.not_imp)(param)


    def task(self, param):
        return self.resp('',
            f"Тест приложения: {date.today().isoformat()}",
            True)


    def rdbm(self, param):
        try:
            with SqlProvider(self) as _sql:
                _sql.qurs.execute(COUNT_TFOMS)
                _tfoms= _sql.qurs.fetchone()
                return self.resp('',
                    f'ТФОМС записей: {_tfoms[0]}', True)
        except Exception as exc:
            return self.abort(400, f'Ошибка БД: {exc}')


    def not_imp(self, param):
        return self.abort(400, f"Метод для '{param}' не реализован")
