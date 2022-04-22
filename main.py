
import os
from pathlib import Path
from poly import create_app

SITE_DIR = Path (os.path.abspath ( os.path.dirname(__file__) ))
#BASE_DIR = os.path.split(SITE_DIR)
STATIC_DIR = SITE_DIR.parent / 'media'
STATIC_DIR = SITE_DIR / 'static'
#sys.path.append(SITE_DIR)
#print('from run.py -> ', STATIC_DIR)

application = create_app(SITE_DIR, STATIC_DIR)

if __name__ == "__main__":
    #app = create_app()
    application.run(debug=True, port=8787)
