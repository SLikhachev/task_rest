import os
from datetime import datetime
#from pathlib import Path
from flask import request, current_app, g
from werkzeug import secure_filename
from poly.reestr.task import RestTask
from poly.reestr.xml.vmx.vmx_sql import to_sql
from poly.utils.files import allowed_file, get_name_tail
from poly.reestr.xml.vmx import config

class XmlVmx(RestTask):

    def __init__(self):
        super().__init__()
        self.task= 'import_errors'

    def this_error(self, file):
        return self.close_task(file, 'Ошибка обработки (подробно в журнале)', False)

    def post(self):

        ts = self.open_task()
        if len(ts) > 0:
            return self.busy(ts)

        self.pack_type= request.form.get('type', 1)

        files= request.files.get('file', None)
        if not bool(files):
            return self.close_task( '', 'Передан пустой запрос на обработку', False)
        
        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reestr', 'vmx')   
        filename = secure_filename(files.filename)
        if not allowed_file( files.filename, current_app.config ) or not filename.endswith('.xml'):
            return self.close_task(filename, "Допустимое расширение имени файла .xml", False)

        lpu, self.smo, ar, self.month = self.parse_xml_name(filename)
        self.year = f'20{ar}'

        # save file to disk
        up_file = os.path.join(catalog, filename)
        files.save(up_file)
        rc= wc= errors= 0
        try:
            rc= to_sql(up_file, ar, ('824',), 'ignore')
        except Exception as e:
            self.abort_task()
            raise e
            current_app.logger.debug(e)
            return self.this_error(filename)

        msg = f'VM файл {filename} Записей считано {rc}. {self.perf()}'
        os.remove(up_file)
        #files.close()

        return self.close_task(filename, msg, True)

    def get(self):
        qonn= current_app.config.db()
        qurs= qonn.cursor()
        qurs.execute(config.COUNT_ERRORS)
        rc= qurs.fetchone()
        
        if not bool(rc[0]):
            return self.out('', 'Нет принятых ошибок', False)
        
        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reestr', 'vmx')   
        df= str(datetime.now()).split(' ')[0]
        filename= f"VM_{df}_{get_name_tail(5)}.csv"
        up_file = os.path.join(catalog, filename)
       
        _q = config.TO_CSV % up_file
        try:
            rc= qurs.execute(_q)
        except Exception as e:
            current_app.logger.debug(e)
            return self.this_error(filename)

        msg = "Посдений файл ошибок"
        return self.out(up_file, msg, True)

'''
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
        return self.result('', msg, detail=detail), current_app.config['CORS']'''
