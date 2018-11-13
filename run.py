#from poly import app
import os
from poly import create_app

SITE_DIR = os.path.abspath ( os.path.dirname(__file__) )
#BASE_DIR = os.path.split(SITE_DIR)
STATIC_DIR = os.path.join(SITE_DIR, 'static')
#DATA_DIR = os.path.split(BASE_DIR)[0]

#print('from run.py -> ', STATIC_DIR)

app = create_app(STATIC_DIR)

if __name__ == "__main__":
    #app = create_app()
    app.run(debug=True, port=8787)
