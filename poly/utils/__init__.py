from flask import Blueprint
from flask_restful import Api

bp = Blueprint('utils', __name__, url_prefix='/utils')
api = Api(bp)

from poly.utils.test import Test
# GET /utils/test
api.add_resource(Test, '/test', endpoint='test')


from poly.utils.files import ListDir, TakeFile
# GET /utils/files/listdir/hosp/csv
api.add_resource(ListDir, '/listdir/<path:dir>/<path:subdir>', endpoint='list_dir')
# POST /utils/file/hosp/csv/22555.csv
# GET DELETE /utils/file/hosp/report/hosp_Июнь.xlsx
api.add_resource(TakeFile,
     '/file/<path:dir>/<path:subdir>',
     '/file/<path:dir>/<path:subdir>/<path:filename>',
    
   
    endpoint='take_file')
