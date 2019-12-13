import os
from datetime import datetime
#from pathlib import Path
from flask import request, current_app, Response
from werkzeug import secure_filename
from flask_restful import Resource
from poly.reestr.xml.vmx.vmx_sql import to_sql
from poly.utils.files import allowed_file
from poly.reestr.xml.vmx import config

class XmlVmx(Resource):

    def result(self, filename, message, done=False):
        return dict(
            file=filename.split('\\')[-1],
            message=message,
            done=done
        )
    
    def post(self):

        time1 = datetime.now()
        type= request.form.get('type', 1)
        files= request.files.get('file', None)
        if files is None:
            return self.result( '', 'Передан пустой запрос на обработку', False), current_app.config['CORS']
        
        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reestr', 'vmx')   
        if files:
            filename = secure_filename(files.filename)
            if not allowed_file( files.filename, current_app.config ) or not filename.endswith('.xml'):
                return self.result(filename, "Допустимое расширение имени файла .xml", False), current_app.config['CORS']

            else:
                # save file to disk
                ym= filename.split('_')[1]
                ya= ym[:2]
                mn= ym[2:]
                up_file = os.path.join(catalog, filename)
                files.save(up_file)
                rc= wc= errors= 0
                try:
                    rc= to_sql(current_app, up_file, ya, [], 'ignore')
                except Exception as e:
                    current_app.logger.debug(e)
                    return self.result(filename, 'Ошибка обработки (подробно в журнале)', False), current_app.config['CORS']
                
                time2 = datetime.now()
                msg = f'VM файл {filename} Записей считано {rc}. Время: {(time2-time1)}'
                os.remove(up_file)
                #files.close()
                
            return self.result(filename, msg, True), current_app.config['CORS']

    def get(self):
        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reestr', 'vmx')   
        df= str(datetime.now()).split(' ')[0]
        filename= f"VM_{df}.csv"
        up_file = os.path.join(catalog, filename)
        qonn= current_app.config.db()
        qurs= qonn.cursor()
        _q = config.TO_CSV % up_file
        try:
            rc= qurs.execute(_q)
        except Exception as e:
            current_app.logger.debug(e)
            return self.result(filename, 'PROCESSING ERROR (see log)', False), current_app.config['CORS']

        msg = "Посдений файл ошибок"
        return self.result(up_file, msg, True), current_app.config['CORS']


class TestSse(Resource):

    def result(self, filename, message, detail=None):
        return dict(
            file=filename.split('\\')[-1],
            message=message,
            detail=detail
        )
    
    def init(self, total=None):
        self.total= 150
        return self.total
    
    def proc(self, coro):
        total= 0
        res= self.result('', '', 0 )
        while total < self.total:
            time.sleep(1.0)
            total += 10 # 15 sec
            res['detail']= total
            coro.send( res )
        res['filename']= 'my_file.zip'
        res['msg']= 'done'
        coro.send( res )
                
    def get(self):
        # this id the Event listener for real processing 
        def coro():
            d= (yield)
            yield f'filename: {d["filename"]} message: {d["message"]} detail: {d["detail"] } '
        
        
        return Respose( coro(), mimetype='text/event-stream', headers=current_app.config['CORS'] )
    
    def post(self):

        time1 = datetime.now()

        """
        try:
            ph, lm, file = make_xml(current_app, year, month, pack, sent)
        except Exception as e:
            current_app.logger.debug(e)
            return self.result('', 'ERROR', detail=None), current_app.config['CORS']
        """
        time2 = datetime.now()
        msg = f'время: {(time2 - time1)} '
        detail= self.init()
        # just return total value to neeed process
        return self.result('', msg, detail=detail), current_app.config['CORS']

