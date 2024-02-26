""" create Flask applcation fn """

import os
from pathlib import Path
import logging
from flask import Flask


env = os.environ.get("FLASK_ENV", default="development")
if env == 'production':
    from poly.config import ProdConfig as Config
else:
    from poly.config import DevConfig as Config

# without Blueprint and factory
#app = Flask(__name__)
#import poly.clinic.views

# with Blueprint and factory
def create_app(site_dir, static_dir, config_class=Config):
    app = Flask(
        __name__,
        instance_path=site_dir / 'instance',
        instance_relative_config=True
    )
    app.config.from_object(config_class)

    # import configs from instance
    if env == 'production':
        app.config.from_pyfile('config_prod.py')
    else:
        app.config.from_pyfile('config_dev.py')

    # folder for files aupload (errors, invoice)
    app.config['UPLOAD_FOLDER'] = os.path.join(static_dir, app.config['DATA_FOLDER'])
    xmldir = Path(app.config['UPLOAD_FOLDER'])
    app.config['BASE_XML_DIR'] = xmldir / 'reestr'

    if app.config.get('LOGGING_FOLDER', None):
        log_file = os.path.join(app.config['LOGGING_FOLDER'], 'applog.log')
    else:
        log_file = os.path.join(static_dir, 'logs', 'applog.log')

    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()
    file_handler.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.DEBUG)

    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    # --- test api ---
    from poly.test import bp as test_bp
    app.register_blueprint(test_bp)

    # http GET for file download
    from poly.utils import bp as utils_bp
    app.register_blueprint(utils_bp)

    # --- reports don't served now ---
    #from poly.report import bp as report_bp
    #app.register_blueprint(report_bp)

    # REST reestr only
    from poly.reestr import bp as reestr_bp
    app.register_blueprint(reestr_bp)

    # --- clinic don't served now ---
    #from poly.clinic import bp as clinic_bp
    #app.register_blueprint(clinic_bp)

    from poly.sprav import bp as sprav_bp
    app.register_blueprint(sprav_bp)

    return app



