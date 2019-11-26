#import os
from datetime import datetime
#from pathlib import Path
from flask import request, current_app
#from werkzeug import secure_filename
from flask_restful import Resource
from poly.utils.fields import month_field
from poly.utils.exept import printException
from poly.reestr.xml.pack.sql_xml import make_xml

class MakeXml(Resource):

    def result(self, filename, message, done=False):
        return dict(
            file=filename.split('\\')[-1] if filename else '' ,
            message=message,
            done=done
        )
    
    def post(self):

        time1 = datetime.now()

        year, month = month_field( request.form.get('month', '') )
        # pack number
        pack = request.form.get('pack', '01')
        # if CHECK is True then don't make reestr xml, check for errors only 
        check = bool( request.form.get('check', None) )
        # if SENT is None ignore already sent, produce full pack
        sent = bool( request.form.get('sent', None) )
        #current_app.logger.debug(year, month, pack, sent)
        try:
            ph, lm, file, errors = make_xml(current_app, year, month, pack, check, sent)
        except Exception as e:
            raise e
            #ex= printException()
            current_app.logger.debug( e )
            return self.result('', f'Исключение: {e}', False), current_app.config['CORS']
        
        time2 = datetime.now()
        if errors:
            msg = f'{ph} PHМ записей, {lm} LM записей, {errors} ошибок, пакет не сформирован : {(time2 - time1)}'
            done = False
        else:
            if check:
                file= None
            msg = f'Сформировано {ph} PHМ записей, {lm} LM записей время: {(time2 - time1)} '
            done= True
            
        return self.result(file, msg, done), current_app.config['CORS']

