
import psycopg2


# Postgres Sql PROVIDER
class SqlProvider(object):

    SET_SCHEMA = 'SET SCHEMA %s'

    def __init__(self, sql_srv: dict):
        dbc = sql_srv or {}
        try:
            self.db = psycopg2.connect(
                port=dbc.get('port', 5432),
                host=dbc.get('host', 'localhost'),
                dbname=dbc['dbname'],
                user=dbc['user'],
                password=dbc['password']
            )
        except KeyError as kex:
            raise AttributeError(f'Inavalid DBC {kex}') from kex
        except psycopg2.Error as pex:
            raise EnvironmentError(f"Can't connect to DB {pex}") from pex
        self.schema=dbc['schema']
        self.inv_table = ''

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.db.close()

    def init_db(self, curs):
        curs.execute(SqlProvider.SET_SCHEMA, (self.schema,))
