import os
import logging
from flask import Flask
from poly.config import DevelopConfig

# without Blueprint and factory
#app = Flask(__name__)
#import poly.clinic.views

# with Blueprint and factory
def create_app(static_dir, config_class=DevelopConfig):

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
    
       
    from poly.utils import bp as utils_bp
    app.register_blueprint(utils_bp)
    
    from poly.report import bp as report_bp
    app.register_blueprint(report_bp)
    
    #from poly.clinic import bp as clinic_bp
    #app.register_blueprint(clinic_bp)
    
    #from poly.sprav import bp as sprav_bp
    #app.register_blueprint(sprav_bp)
    
    return app
    
    

