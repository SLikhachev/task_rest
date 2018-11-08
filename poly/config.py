
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
    ALLOWED_EXTENSIONS = set(['txt','rar','zip','7zip', 'csv', 'xlsx'])
    ALLOWED_EIR_FILE = set(['csv'])
    IGNORED_FILES = set(['.gitignore'])
    CORS = {'Access-Control-Allow-Origin': '*'}
    MONTH = ['Январь', 'Февраль', 'Март',
             'Апрель', 'Май', 'Июнь',
             'Июль', 'Август', 'Сентябрь',
             'Октябрь', 'Ноябрь', 'Декабрь']
   
class DevelopConfig(BaseConfig):
    'Development environment specific config'
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'Another random secret key'

"""
class StagConfig(BaseConfig):
    'Staging specific config'
    DEBUG = True

class ProductConfig(BaseConfig):
    'Production specific config'
    DEBUG = False
    SECRET_KEY = open('help/sk.txt').read()
"""    


