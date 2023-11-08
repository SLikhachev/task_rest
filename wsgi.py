"""
    WSGI application for run Flask app in production as gunicorn process

    Prefferd way to start is place this file in parent directory

"""
import os, sys
from main import application as webapp

BASE_DIR = os.path.dirname(__file__)
#SITE_DIR = os.path.join(BASE_DIR, 'webapp')
sys.path.append(BASE_DIR)
#sys.path.append(SITE_DIR)


application= webapp
