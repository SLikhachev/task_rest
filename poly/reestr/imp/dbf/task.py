import os
from datetime import datetime
#from pathlib import Path
from flask import request, current_app
from werkzeug import secure_filename
from flask_restful import Resource
from poly.utils.fields import month_field
from poly.reestr.imp.dbf.make_import import dbf_to_sql as to_sql

class ImportDbf(Resource):

    def result(self, filename, message, done):
        file = None
        if bool(filename) and len(filename) > 0:
            file= filename.split('\\')[-1]
        return dict(
            file=file,
            message=message,
            done=done 
        )
    
    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_DBF_FILE']
    
    def post(self):

        time1 = datetime.now()

        tst = request.form.get('test', None)
        year, month = month_field( request.form.get('month', '') )

        files = request.files.get('file', None)
        if files is None:
            return self.result( 'Нет файла ', 'Передан пустой запрос на обработку', False), current_app.config['CORS']
        
        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reestr', 'dbf')
        if files:
            filename = secure_filename(files.filename)
            if not self.allowed_file(files.filename):
                return self.result(filename, " File type not allowed", False), current_app.config['CORS']

            else:
                # save file to disk
                up_file = os.path.join(catalog, filename)
                files.save(up_file)
                
                test = 1 if tst else 0
                rc, wc, err, detail = to_sql(current_app, catalog, filename,  month, year, test)
                #current_app.logger.debug(f'{rc} {wc} {err} {detail}')
                msg = 'Импорт: ' if test == 0 else 'Тест: '
                time2 = datetime.now()
                msg += f'считано: {rc}, записано: {wc}, ошибок: {err}, время: {(time2 - time1)}'
                os.remove(up_file)

            return self.result(filename, msg, True), current_app.config['CORS']

