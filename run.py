#from poly import app
import os
from pathlib import Path
from poly import create_app

SITE_DIR = Path (os.path.abspath ( os.path.dirname(__file__) ))
#BASE_DIR = os.path.split(SITE_DIR)
#STATIC_DIR = os.path.join(SITE_DIR, 'static')
STATIC_DIR = SITE_DIR.parent / 'media'

#print('from run.py -> ', STATIC_DIR)

app = create_app(STATIC_DIR)

if __name__ == "__main__":
    #app = create_app()
    app.run(debug=True, port=8787)
