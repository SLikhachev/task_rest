
#from types import SimpleNamespace as NS
#import psycopg2
from barsxml.sql import get_sql_provider

# Postgres Sql PROVIDER
class SqlProvider:
    """ SQL connection class can be used as context manager """

    def __init__(self, config):
        """ @params:
            config where:
                :sql: object - sql provider definition
                :mo_code: str(6) - full MO code e.g. '250747'
                :_year: str(2) - year of the report last 2 digits
                :month: str(2) - month ot report '01'-'12'
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
        self._sql = None

    def connect(self):
        """ create sql connection """
        if not self._sql:
            self._sql = get_sql_provider(self).SqlProvider(self)
        # self.qurs =
        #   self._db.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        return self._sql # sql object.(_db: Connection, qurs: Cursor)

    def close(self):
        """ close sql connection """
        if self._sql:
            self._sql._db.close()

    def commit(self):
        # commit pending transactions
        self._sql._db.commit()

    # to use the class as context manager
    def __enter__(self):
        return self.connect() # returns SQL object not DB.connection

    def __exit__(self, type, value, traceback):
        self.commit()
        self.close()

