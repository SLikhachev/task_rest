import os
import logging
import psycopg2
from flask import Flask
#from poly.config import DevelopConfig
from poly.config import Lpu228Config as Config
#from poly.config import Lpu796Config as Config

# without Blueprint and factory
#app = Flask(__name__)
#import poly.clinic.views

# with Blueprint and factory
def create_app(static_dir, config_class=Config):

    app = Flask(__name__)
    #print(config_class.IGNORED_FILES)
    
    app.config.from_object(config_class)
    #print(app.config['IGNORED_FILES'])
    #app.config['UPLOAD_FOLDER'] = os.path.abspath( os.path.join(data_dir, 'data') )
    app.config['UPLOAD_FOLDER'] = os.path.join(static_dir, app.config['DATA_FOLDER'])
    #print('from app create -> ', static_dir)
    #print('from app create -> ', app.config['UPLOAD_FOLDER'])
    log_file = os.path.join(static_dir, app.config['LOGGING_FOLDER'], 'my_log.log')
    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()
    file_handler.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.DEBUG)

    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    app.config['DB_CONF'] = 'dbname=%s user=%s password=%s' % (
        app.config['DB_NAME'], app.config['DB_USER'], app.config['DB_PASS']
    )
    app.config.db = lambda: psycopg2.connect(app.config['DB_CONF'])
       
    from poly.utils import bp as utils_bp
    app.register_blueprint(utils_bp)
    
    from poly.report import bp as report_bp
    app.register_blueprint(report_bp)

    from poly.reestr import bp as reestr_bp
    app.register_blueprint(reestr_bp)
    #from poly.clinic import bp as clinic_bp
    #app.register_blueprint(clinic_bp)
    
    #from poly.sprav import bp as sprav_bp
    #app.register_blueprint(sprav_bp)
    
    return app
    
    

