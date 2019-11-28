
class BaseConfig(object):
    
    'Base config class'
    SECRET_KEY = 'A random secret key'
    DEBUG = True
    TESTING = False
    NEW_CONFIG_VARIABLE = 'my value'
    DATA_FOLDER = 'data'
    LOGGING_FOLDER = 'logging'
    UPLOAD_FOLDER = ''
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024 # 50MB
    ALLOWED_EXTENSIONS = set(['txt','rar','zip','7z', 'csv', 'xlsx', 'xml'])
    ALLOWED_EIR_FILE = set(['csv'])
    ALLOWED_DBF_FILE = set(['dbf'])
    IGNORED_FILES = set(['.gitignore'])
    CORS = {'Access-Control-Allow-Origin': '*'}
    MONTH = ('Январь', 'Февраль', 'Март',
             'Апрель', 'Май', 'Июнь',
             'Июль', 'Август', 'Сентябрь',
             'Октябрь', 'Ноябрь', 'Декабрь')
   
class Lpu228Config(BaseConfig):
    'Development environment specific config'
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'Another random secret key'
    MO_CODE = ('228', '229')
    DB_NAME = 'prive'
    DB_USER = 'postgres'
    DB_PASS = 'boruh'
    OGRN= ''
    
class Lpu796Config(BaseConfig):
    'Development environment specific config'
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'Another random secret key'
    MO_CODE = ('796',)
    DB_NAME = 'hokuto'
    DB_USER = 'postgres'
    DB_PASS = 'boruh'
    OGRN= '1112539013696'


"""
class StagConfig(BaseConfig):
    'Staging specific config'
    DEBUG = True

class ProductConfig(BaseConfig):
    'Production specific config'
    DEBUG = False
    SECRET_KEY = open('help/sk.txt').read()
"""    


