
# place this demo file to ../instance folder, then edit it
import os

SECRET_KEY =  'instance secret key'
JWT_TOKEN_SECRET = 'instance jwt secret'

# SQL provider string
SQL_PROVIDER = 'pgrest'
SQL_PROVIDER = 'postgres'

# 1st provider definition
PGREST = { 'srv': os.environ.get('DB_SRV', default='http://localhost:7000')}

# 2nd provider
POSTGRES = dict(
    port=os.getenv('DB_PORT') or 5432,
    host=os.getenv('DB_HOST') or '127.0.0.1',
    dbname = os.getenv('DB_NAME') or 'dbname',
    user=os.getenv('DB_USER') or 'postgres',
    password=os.getenv('DB_PASSWORD') or 'dbpass',
    schema=os.getenv('DB_SCHEMA') or 'public',
    dbauth=os.getenv('DB_AUTH') or 'no'
)

#dict for registered MO
#key mo_code_long: (ogrn, )
STUB_MO_CODE= '000000'
MOS = {
    '000000': ('0000000000000',),
    '250796': ('1112539013696',)
}

LOGGING_FOLDER = "/home/user/folder/www/logs/task_rest"