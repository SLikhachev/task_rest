""" definition of RestTask class """

from typing import Tuple
import os, re
from datetime import date
from time import perf_counter

from flask_restful import Resource, fields, marshal
from flask import request, make_response, current_app

from poly.utils.parse_jwt import parse_jwt_token


response_json = {
    'file': fields.String,
    'message': fields.String,
    'done': fields.Boolean,
}

# tail of the common files' names
tail = r'_(?P<year>\d{2})(?P<month>\d{2})(?P<lpu>\d{3})'

# headr of the common files' names
fnames= dict(
# errors file name: FHТ25М250796_21107961.xml
    errs=re.compile(r'^(?:\w{6})(?P<mo_code>\d*)' + tail),

# invoice files' names
# invoice to the TFOMS: HM250796T25_22027961.zip
# invoice to the SMO: HM250796S25011_211079610.zip
    invs=re.compile(r'(?:\w{2})(?P<mo_code>\d*)[S,T](?P<smo>\d*)' + tail)
)

class RestTask(Resource):
    """ class definition """

    def __init__(self):
        super().__init__()
        self.year= None
        self.month= None
        self.smo= None
        self.pack_num= None
        self.pack_type= None
        self.this_year= date.today().year
        self.this_month= date.today().month
        self.time1 = perf_counter()
        # string value
        self.SQL_PROVIDER = current_app.config['SQL_PROVIDER']
        self.sql_provider = self.SQL_PROVIDER
        # dict value
        self.sql_srv = current_app.config[self.SQL_PROVIDER.upper()]
        self.sql = self


    def dispatch_request(self, *args, **kwargs):

        # get/post analyzed only
        if request.method not in ['GET', 'POST']:
            return super().dispatch_request(*args, **kwargs)

        #print(f'root: {request.root_path}, path: {request.path}')
        if request.path.startswith('/test'):
            return super().dispatch_request(*args, **kwargs)

        role = user = None

        # authorize user with DB
        auth=os.getenv('DB_AUTH')
        secret=os.getenv('JWT_TOKEN_SECRET')

        dev = os.getenv('FLASK_ENV')
        if dev == 'development':
            print(f'dev auth: {auth}, secret: {secret}')

        #if self.sql_srv.get('dbauth', 'no') == 'yes':
        if auth == 'yes' and secret is not None:
            # may be authorized request
            status, role, user = parse_jwt_token(
                request.headers.get('Authorization', None),
                secret
            )
            # check status
            if status != 200:
                response = make_response(role)
                response.status = status
                return response

        # dispatch request
        self.sql_srv['provider'] = self.sql_provider
        self.sql_srv['role']=role
        self.sql_srv['cuser']=user
        if dev == 'development':
            print(f'dev role: {role}, user: {user}')
        return super().dispatch_request(*args, **kwargs)


    def options(self):
        """ return response to OPTIONS request """
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,  GET,  POST'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization'
        return response


    def catalog(self, base: str, *args):
        """ @params
            :base: str - name of the base in config object
            return path to the upload folder
        """
        if len(base) == 0:
            base = 'UPLOAD_FOLDER'
        return  os.path.join(current_app.config[base], *args)


    def parse_fname(self, _name: str, _type: str) -> Tuple[str]:
        """ @params:
            :_name: str - name of the file
            :_type: str - key in fnames dict ('errs', 'invs')
            return tuple of (
                'mo_code':str(6),
                'lpu': str(3),
                'smo': int,
                'year': str(2),
                'month': str(2)
            ) | error: str
        """
        try:
            # AttributeError
            m = fnames[_type].search(_name).groupdict()
            # KeyError, ValueError
            _smo = m.get('smo', None)
            if _type=='invs' and not _smo:
                return f'В имени файла счета {_name} нет smo'
            smo = int(m['smo'] if len(m['smo']) > 2 else '0') if _smo else 0
            return m['mo_code'], m['lpu'], smo, \
               m['year'], m['month']
        except Exception:
            return ''
            #return f'Имя {_name} не соответсвует шаблону: {e}'

    def perf(self):
        return f'Время: {round( (perf_counter() - self.time1), 2)} cek.'

    def fname(self, file):
        """ get file name from path """
        f = os.path.basename(file)
        if bool(f) and len(f) > 0:
            return f
        return ''

    def result(self, filename, message, done=False):
        """ make result dict"""
        return {
            'file': self.fname(filename),
            'message': f'{message} {self.perf()}',
            'done': done
        }

    def resp(self, file: str, msg: str, done: bool):
        """ return JSON payload for rsponse """
        _ma = marshal(self.result(file, msg, done), response_json)
        return _ma, 200, current_app.config['CORS']

    def abort(self, code: int, msg: str):
        """ return JSON payload for rsponse with error code """
        current_app.logger.debug(msg)
        return marshal(self.result('', msg, False), response_json), code, current_app.config['CORS']