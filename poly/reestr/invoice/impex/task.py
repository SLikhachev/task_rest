import os
from datetime import datetime
from pathlib import Path
from flask import request, current_app, Response, g
from werkzeug import secure_filename
from poly.reestr.task import RestTask
#from flask_restful import Resource
from poly.reestr.invoice.impex.imp_inv import imp_inv
from poly.reestr.invoice.impex.exp_usl import exp_usl
from poly.reestr.invoice.impex.exp_inv import exp_inv
from poly.reestr.invoice.impex.correct_ins import correct_ins
from poly.reestr.invoice.impex import config 
from poly.utils.files import allowed_file


class InvImpex(RestTask):

    def post(self):
        # here typ field is used
        self.get_task = config.GET_INV_TASK
        self.set_task = config.SET_INV_TASK

        typ= int( request.form.get('type', 1) )
        # correct smo flag 
        csmo= False
        if request.form.get('csmo', '') == 'on':
            csmo= True
        
        #  TYP field as flag
        ts = self.open_task(typ)
        if len( ts ) > 0:
            return self.out('', ts, False)

        #qurs.close()

        files= request.files.get('file', None)
        if not bool(files):
            return self.close_task('', 'Передан пустой запрос на обработку', False)
        
        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reestr', 'inv')
        filename = secure_filename(files.filename)
        fp= Path(filename)

        if not allowed_file( files.filename, current_app.config ) or fp.suffix != '.zip':
            return self.close_task(filename, " Допустимый тип файла .zip", False)
        
        #test 
        #return self.close_task( filename, f'typ {typ} , csmo {csmo}', False  )

        # save file to disk
        up_file = os.path.join(catalog, filename)
        files.save(up_file)
        rc= wc= errors= 0

        dc = (0,)

        try:
            res= imp_inv(current_app, up_file, typ)
            if len(res) == 1:
                current_app.logger.debug( config.FAIL[ abs( res[0] ) ] )
                return self.close_task('', config.FAIL[ abs( res[0] ) ], False)

            rc, smo, mon, yar= res
            if typ == 6:
                #return self.result('', 'Импорт выполнен', True), current_app.config['CORS']
                wc, xreestr = exp_usl(current_app, smo, mon, yar, catalog)
            else:
                if csmo:
                    dc= correct_ins(smo, mon, yar)
                wc,  xreestr= exp_inv(current_app, smo, mon, yar, typ, catalog)
        except Exception as e:
            self.abort_task()
            raise e
            current_app.logger.debug(e)
            return self.close_task(filename, 'Ошибка сервера (детали в журнале)', False)
       
        #msg = f'Счет {filename} Записей считано {rc}. Время: {(time2-time1)}'
        msg = f'Счет {filename} Записей в счете {rc}, записей в реестре {wc}. \
            Испр. СМО: {dc[0]}. {self.perf()}'
        os.remove(up_file)

        return self.close_task(xreestr, msg, True)

    def get(self):
        raise NotImplemented

# future implementation
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
