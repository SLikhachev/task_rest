# --*-- coding='UTF-8' --*--

#import os
import psycopg2
from datetime import date
#from pathlib import Path
from flask import request, current_app
from flask_restful import Resource
from .polic_146_sql import FillReportTable
from .volum_report import make_report

class MakeReport(Resource):

    def result(self, filename, message, done):
        return dict(
            file=filename.split('\\')[-1],
            message=message,
            done=done 
        )
    
    def post(self):
        # fill report 146 table
        test = request.form.get('test', None)
        write_flag = True
        if test:
            write_flag=False

        dm = request.form.get('month', '')
        if dm != '':
            dm = [ int(s) for s in dm.split('-') ]
        else:
            dm = [ int(s) for s in date.today().isoformat().split('-')]
        year, month = dm[0], dm[1]
        msg = "Рассчет объемов за %s %s -- " % (current_app.config['MONTH'][month-1], year)
        qonn = psycopg2.connect("dbname=prive user=postgres password=boruh")
        #__init__(self, app, db, mo, month, year, stom=False, stac=False, write=False):
        
        fill_rep_ambul = FillReportTable(current_app, qonn, '228', month, year, stom=True, stac=True, write=write_flag)
        #fill_rep.test()
        if fill_rep_ambul.table_test():
            msg += fill_rep_ambul.set_total_ambul()
        else:
            msg += ' Не найден отчет поликлиники %s ' % fill_rep_ambul.rr_table
        del fill_rep_ambul
        
        fill_rep_travm = FillReportTable(current_app, qonn, '229', month, year, write=write_flag)
        if fill_rep_travm.table_test():
            msg += fill_rep_travm.set_total_travm()
        else:
            msg += ' Не найден отчет трвавмпункта %s ' % fill_rep_travm.rr_table
        del fill_rep_travm
        # return { msg: "String", done: "bool" }
        return self.result('', msg, False), current_app.config['CORS']

    def get(self):
        dm = request.args.get('month', '')
        if dm != '':
            dm = [ int(s) for s in dm.split('-') ]
        else:
            dm =  [ int(s) for s in date.today().isoformat().split('-')]
        year, month = dm[0], dm[1]
        qonn = psycopg2.connect("dbname=prive user=postgres password=boruh")
        report = make_report(current_app, qonn, month, year)

        msg = "Объемы за %s %s" % (current_app.config['MONTH'][month-1], year)
        return self.result(report, msg, True), current_app.config['CORS']

