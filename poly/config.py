
class BaseConfig(object):
    
    'Base config class'
    SECRET_KEY =  'Rwhbye6453mnlkhgtfbdl8893kbctrwmhmfytrbvxzds'
    DEBUG = True
    TESTING = True
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

class DevConfig(BaseConfig):
    'Staging specific config'

class ProdConfig(BaseConfig):
    'Production specific config'
    DEBUG = False
    TESTING = False



