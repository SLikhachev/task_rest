""" definition of RestTask class
    as a base for all other Tasks classes
"""

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

# the tail of the common files' names
tail = r'_(?P<year>\d{2})(?P<month>\d{2})(?P<lpu>\d{3})'

# the header of the common files' names
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
        """
        Override Resource's dispatch_request method to filter only GET and POST requests,
        check if the request is authorized and dispatch the request to the parent class.
        The request is authorized if the JWT token is valid and the user has the role
        specified in the token.
        """
        # get/post analyzed only
        if request.method not in ['GET', 'POST']:
            return super().dispatch_request(*args, **kwargs)

        #print(f'root: {request.root_path}, path: {request.path}')
        if request.path.startswith('/test'):
            return super().dispatch_request(*args, **kwargs)

        role = user = None

        # authorize user with DB
        auth=os.getenv('DB_AUTH') or 'no'
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
        """
        Return response to OPTIONS request

        This method is used to handle OPTIONS requests. It sets the
        required headers for CORS to work.

        Returns:
            flask.Response: response to OPTIONS request
        """
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = "*"
        response.headers['Access-Control-Allow-Methods'] = "OPTIONS,  GET,  POST"
        response.headers['Access-Control-Allow-Headers'] = \
            "Authorization, Origin, X-Requested-With, Content-Type, Accept"
        response.headers['Referrer-Policy'] = "unsafe-url"  # (не рекомендуется для продакшена)
        #response.headers['Referrer-Policy'] = "no-referrer-when-downgrade"
        # В html SPA добавить
        #<meta name="referrer" content="no-referrer-when-downgrade">.
        return response

    def catalog(self, base: str, *args: str) -> str:
        """
        @brief: Build full path to the upload folder
        @param base: str - name of the base in config object
        @param *args: str - path components to join
        @return: str - full path to the upload folder
        """
        if len(base) == 0:
            base = 'UPLOAD_FOLDER'

        # join path components
        path = os.path.join(current_app.config[base], *args)

        # return full path
        return path

    def parse_fname(self, _name: str, _type: str) -> Tuple[str]:
        """
        Parse filename and extract mo_code, lpu, smo, year, month

        @param _name: str - name of the file
        @param _type: str - key in fnames dict ('errs', 'invs')
        @return: tuple of (
            'mo_code': str(6),
            'lpu': str(3),
            'smo': int,
            'year': str(2),
            'month': str(2)
        ) | error: str
        """
        try:
            # search filename for mo_code, lpu, smo, year, month
            m = fnames[_type].search(_name).groupdict()
            # check if smo is present
            _smo = m.get('smo', None)
            if not _smo and _type == 'invs':
                return f'В имени файла счета {_name} нет smo'
            # try to convert smo to int
            smo = int(m['smo'] if len(m['smo']) > 2 else '0') if _smo else 0
            # return tuple of mo_code, lpu, smo, year, month
            return m['mo_code'], m['lpu'], smo, \
                   m['year'], m['month']
        except AttributeError:
            # fnames[_type] does not exist
            return f'No pattern for {_type} in fnames dict'
        except KeyError as e:
            # key not found in match object
            return f'Key not found in match object: {e}'
        except ValueError:
            # smo is not a valid int
            return f'smo is not a valid integer'

    def perf(self):
        return f'Время: {round( (perf_counter() - self.time1), 2)} cek.'

    def fname(self, file: str) -> str:
        """
        Get the file name from a path.

        @param file: str - the path to the file
        @return: str - the file name
        """
        # get the file name from the path
        f = os.path.basename(file)
        # return the file name if it is not empty
        if bool(f) and len(f) > 0:
            return f
        # return an empty string if the file name is empty
        return ''

    def result(self, filename, message, done=False):
        """ make result dict"""
        return {
            'file': self.fname(filename),
            'message': f'{message} {self.perf()}',
            'done': done
        }

    def resp(self, file: str, msg: str, done: bool):
        """
        Return JSON payload for response.

        @param file: str - the file name
        @param msg: str - the message to be returned
        @param done: bool - whether the file has been processed successfully
        @return: tuple of (JSON payload, HTTP status code, CORS config)
        """
        # marshal the result to a JSON object
        _ma = marshal(self.result(file, msg, done), response_json)
        # return the JSON object, HTTP status code, and CORS config
        return _ma, 200, current_app.config['CORS']

    def abort(self, code: int, msg: str) -> Tuple[dict, int, dict]:
        """
        Return JSON payload for response with error code.

        @param code: int - HTTP status code
        @param msg: str - the message to be returned
        @return: tuple of (JSON payload, HTTP status code, CORS config)
        """
        # log the message at DEBUG level
        current_app.logger.debug(msg)
        # marshal the result to a JSON object
        _ma = marshal(self.result('', msg, False), response_json)
        # return the JSON object, HTTP status code, and CORS config
        return _ma, code, current_app.config['CORS']
