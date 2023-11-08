""" Main application module for task_rest app

    Used for run flask app locally as alternative to run.py file
    or mainly in production with WSGI app

"""

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
#sys.path.append(SITE_DIR)
#print('from run.py -> ', STATIC_DIR)

application = create_app(SITE_DIR, STATIC_DIR)

if __name__ == "__main__":
    #app = create_app()
    application.run(debug=True, port=8787)
