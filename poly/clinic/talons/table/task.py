""" defines a class for task to cretae new talons table """

import datetime

from flask import current_app

from poly.utils.sqlbase import SqlProvider
from poly.task import RestTask
from poly.clinic.talons.table import config as cfg

class CreateTalonsTable(RestTask):
    """ class def """
    def __init__(self):
        super().__init__()
        self.tmp_dir= None
        # these params we need for sql_adpater's compatabilies
        self.mo_code = current_app.config.get('ACTUAL_MO_CODE', '000000')
        self.now = datetime.datetime.now()
        self._year= self.now.year

    # upload csv file and process data
    def post(self):
        current_year = self._year % 100
        next_year = current_year
        current_month = self.now.month
        if current_month < 12:
            # if table for current year not exista, create it
            # this will work upto december of the current year
            current_year -= 1
        else:
            # a table for the next year we can craete in december
            next_year += 1
        try:
            with SqlProvider(self) as _sql: # object.(_db: Connection, qurs: NamedTupleCursor)
                _sql.qurs.execute(cfg.GET_TALONZ_TABLES)
                _tables = _sql.qurs.fetchall()
                if all(
                    (t[0] != f"{cfg.TBL}{current_year}" for t in _tables)
                ):
                    return self.resp('', f"Таблицы образца {cfg.TBL}{current_year} не существует", False)
                if any(
                    (t[0] == f"{cfg.TBL}{next_year}" for t in _tables)
                ):
                    return self.resp('', f"Таблица назначения {cfg.TBL}{next_year} уже существует", False)
                _sql.qurs.execute(cfg.COPY_TALONZ_TABLE, (current_year, next_year, False))
        except Exception as exc:
            raise exc
            #return self.abort(500, f"Ошибка сервера: {exc}")
        msg = f"Cоздана таблица: {cfg.TBL}{next_year}"
        return self.resp('', msg, True)

