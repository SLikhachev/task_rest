
#import psycopg2
from barsxml.sql import get_sql_provider

# Postgres Sql PROVIDER
class SqlProvider(object):

    def __init__(self, config, mo_code, year, month):
        """ init """
        """ get provider class """
        self.SQL_PROVIDER= config['provider']
        self.SQL_SRV = config
        self.ERRORS_TABLABLE_NAME = config['errors_table']
        self.mo_code = mo_code
        self.year = year
        self.month = month
        self.inv_table = ''

    def __enter__(self):
        self.sql = get_sql_provider(self).SqlProvider(
            self, self.mo_code, self.year, self.month
        )
        return self.sql

    def __exit__(self, type, value, traceback):
        self.sql.close()

