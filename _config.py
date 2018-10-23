
class BaseConfig(object):
    'Base config class'
    SECRET_KEY = 'A random secret key'
    DEBUG = True
    TESTING = False
    NEW_CONFIG_VARIABLE = 'my value'

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


