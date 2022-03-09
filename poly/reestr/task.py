
import os, re
from datetime import date
from time import perf_counter
from flask import request, make_response, current_app
from flask_restful import Resource, fields, marshal
from poly.utils.parse_jwt import parse_jwt_token


res_fields = {
    'file': fields.String,
    'message': fields.String,
    'done': fields.Boolean,
}

tail = '_(?P<year>\d{2})(?P<month>\d{2})(?P<lpu>\d{3})'
fnames= dict(
# FHТ25М250796_21107961.xml
    errs=re.compile("^(?:\w{6})(?P<mo_code>\d*)" + tail),
# HM250796T25_22027961.zip
# HM250796S25011_211079610.zip
    invs=re.compile("(?:\w{2})(?P<mo_code>\d*)[S,T](?P<smo>\d*)" + tail)
)

class RestTask(Resource):

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
        self.sql_provider = current_app.config['SQL_PROVIDER']
        self.sql_srv = current_app.config[self.sql_provider.upper()]
        self.role = ''
        self.user = ''

    def dispatch_request(self, *args, **kwargs):
        if request.authorization:
            status, self.role, self.user = parse_jwt_token(
                request.authorization.to_header(), current_app.config['JWT_TOKEN_SECRET']
            )
            if status != 200:
                response = make_response(self.role)
                response.status = status
                return response

        return super().dispatch_request(*args, **kwargs)

    def options(self, *args, **kwargs):
        """ return respose to OPTIONS request """
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,  GET,  POST'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization'
        return response

    def catalog(self, base, *args):
        if len(base) == 0:
            base = 'UPLOAD_FOLDER'
        return  os.path.join(current_app.config[base], *args)

    def parse_fname(self, name: str, type: str):#  -> list:
        try:
            # AttributeError
            m = fnames[type].search(name).groupdict()
            # KeyError, ValueError
            smo = int(m['smo'] if len(m['smo']) > 2 else '0')
            return m['mo_code'], m['lpu'], smo, \
               m['year'], m['month']
        except:
            return ()

    def perf(self):
        return f'Время: {round( (perf_counter() - self.time1), 2)} cek.'

    def fname(self, file):
        f = os.path.basename(file)
        if bool(f) and len(f) > 0:
            return f
        return ''

    def result(self, filename, message, done=False):
        return dict(
            file=self.fname(filename),
            message=f'{message} {self.perf()}',
            done=done
        )

    def resp(self, file, msg, done):
        return marshal(self.result(file, msg, done), res_fields), 200, current_app.config['CORS']

    def abort(self, code, msg ):
        current_app.logger.debug(msg)
        return marshal(self.result('', msg, False), res_fields), code, current_app.config['CORS']