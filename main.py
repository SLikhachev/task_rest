#from poly import app
import os
from pathlib import Path
from poly import create_app

SITE_DIR = Path (os.path.abspath ( os.path.dirname(__file__) ))
#BASE_DIR = os.path.split(SITE_DIR)
STATIC_DIR = SITE_DIR.parent / 'media'
STATIC_DIR = SITE_DIR / 'static'

#print('from run.py -> ', STATIC_DIR)

app = create_app(SITE_DIR, STATIC_DIR)

if __name__ == "__main__":
    #app = create_app()
    app.run(debug=True, port=8787)
