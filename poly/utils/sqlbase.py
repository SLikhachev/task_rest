
from types import SimpleNamespace as NS
#import psycopg2
from barsxml.sql import get_sql_provider

# Postgres Sql PROVIDER
class SqlProvider(object):

    def __init__(self, config):
        """ @param: config where:
                sql: object - sql provider definition
                mo_code: str(6) - full MO code e.g. '250747'
                _year: str(2) - year of the report last 2 digits
                month: str(2) - month ot report '01'-'12'
        """
        #assert hasattr(config, 'sql'), "SQL provider нет атрибута sql"
        assert hasattr(config.sql, 'sql_provider'), "SQL provider нет атрибута sql_provider"
        assert hasattr(config.sql, 'sql_srv'), "SQL provider нет атрибута sql_srv"
        self.SQL_PROVIDER=config.sql.sql_provider # String
        self.sql_srv = config.sql.sql_srv
        self.mo_code = config.mo_code
        self.ye_ar = config._year
        self.month = config.month
        self.inv_table = ''
        self.errors_table=config.sql.sql_srv.get('errors_table', 'None')

    def __enter__(self):
        self._sql = get_sql_provider(self).SqlProvider(self)
        return self._sql

    def __exit__(self, type, value, traceback):
        self._sql.close()

