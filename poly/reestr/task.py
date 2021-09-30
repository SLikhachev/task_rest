
from datetime import date
from time import perf_counter
import requests
from flask import current_app
from flask_restful import Resource, fields, marshal

res_fields = {
    'file': fields.String,
    'message': fields.String,
    'done': fields.Boolean,
}


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

    def parse_xml_name(self, name: str) -> tuple:
        
        nlist= name.split('_')
        hdr, tail= nlist[0], nlist[1]
        s= hdr.find('S') + 1
        if s <= 0:
            smo= 0
        else:
            smo= int( hdr[s:] ) #int 25016
        if len(tail) < 7:
            return ()
        lpu= tail[4:7] # str 796
        year= tail[:2] # str 20
        month= tail[2:4] #  str 01
        #print( lpu: str(3), smo: int, year: str(2), month: str(2))
        return lpu, smo, year, month

    def perf(self):
        return f'Время: {round( (perf_counter() - self.time1), 2)} cek.'

    def fname(self, file):
        if bool(file) and len(file) > 0:
            return file.split('\\')[-1]
        return ''

    def result(self, filename, message, done=False):
        return dict(
            file=self.fname(filename),
            message=f'{message} {self.perf()}',
            done=done
        )

    def resp(self, file, msg, done):
        return marshal(self.result(file, msg, done), res_fields), 200, current_app.config['CORS']
