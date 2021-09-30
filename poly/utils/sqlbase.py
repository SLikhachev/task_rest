
import psycopg2


# Postgres Sql PROVIDER
class SqlProvider(object):

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
        except KeyError as e:
            raise AttributeError(f'Inavalid DBC {e}')
        except psycopg2.Error as e:
            raise EnvironmentError(f"Can't connect to DB {e}")

    def __enter__(self):
        return self.db

    def __exit__(self, type, value, traceback):
        self.db.close()
