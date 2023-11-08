""" Run Flask application locally in development mode

    To run you should:
    1. run script flask_conf_local.sh with actual environment variables
    2. run script runs.sh

    Then you may tests the app or check of running with omslite service

"""

#from poly import app
import os
from pathlib import Path
from poly import create_app

# SITE_DIR is absolute sys path to this directory
SITE_DIR = Path (os.path.abspath ( os.path.dirname(__file__) ))
#BASE_DIR = os.path.split(SITE_DIR)

# STATIC_DIR is absolute path to static directory where we store
# STATIC_DIR/data directory with actual files to work with
STATIC_DIR = SITE_DIR.parent / 'media'
STATIC_DIR = SITE_DIR / 'static'

#print('from run.py -> ', STATIC_DIR)

app = create_app(SITE_DIR, STATIC_DIR)

if __name__ == "__main__":
    #app = create_app()
    app.run(debug=True, host='127.0.0.1', port=8787)
