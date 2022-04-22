
import os, sys
from main import application

BASE_DIR = os.path.dirname(__file__)
SITE_DIR = os.path.join(BASE_DIR, 'webapp')
sys.path.append(BASE_DIR)
sys.path.append(SITE_DIR)


application= application
