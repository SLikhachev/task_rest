import os
from datetime import date
#from pathlib import Path
from flask import request, current_app
from werkzeug import secure_filename
from flask_restful import Resource
from .hosp_class import HospEir
from .csv_to_sql import csv_to_sql
from .hosp_report import make_report

class TakeCsv(Resource):
    def get(self):
        return {'task': 'take csv'}

class MakeReport(Resource):
    
    def result(self, filename, message, done):
        return dict(
            file=filename.split('\\')[-1],
            message=message,
            done=done 
        )
    
    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EIR_FILE']
    
    def post(self):
        
        tst = request.form.get('test', None)
        
        dm = request.form.get('month', "")
        if dm != "":
            dm = dm.split('-')
        else:
            dm = [ int(s) for s in date.today().isoformat().split('-')]
        year, month = dm[0], dm[1]
        
        files = request.files.get('file', None)
        if files is None or files == '':
            return self.result( 'Нет файла ', 'Передан пустой запрос на обработку', False), current_app.config['CORS']
        
        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], 'hosp', 'csv')   
        filename = secure_filename(files.filename)
        if not self.allowed_file(files.filename):
            return self.result(filename, " File type not allowed", False), current_app.config['CORS']

        # save file to disk
        up_file = os.path.join(catalog, filename)
        files.save(up_file)

        test = 1 if tst else 0
        """
     try:
         test, rc, wc, errors = csv_to_sql(current_app, up_file, HospEir, test, clear=True)
     except Exception as e:
         current_app.logger.debug(e)
         raise e
         #return self.result('', f'Исключение: {e}', False), current_app.config['CORS']
     """

        test, rc, wc, errors = csv_to_sql(current_app, up_file, HospEir, test, clear=True)

        msg = 'Режим обработки файла '
        if test > 0:
            msg = 'Тестовый режим '
        if errors > 0:
            msg += 'обнаружено ошибок %s (игнорируем) ' % errors
        msg += 'обработано записей %s' % rc
        current_app.logger.debug(msg)

        if test > 0: #or errors > 0:
            os.remove(up_file)
            return self.result(filename, msg, False), current_app.config['CORS']


        report = make_report(current_app, year, month)
        msg = 'Обработан файл %s Записей считано %s, записано %s. Ошибок %s (игнорируем)' % (
            filename, rc, wc, errors)
        os.remove(up_file)
        #files.close()

        return self.result(report, msg, True), current_app.config['CORS']

