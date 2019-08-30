import os
from datetime import datetime
#from pathlib import Path
from flask import request, current_app
#from werkzeug import secure_filename
from flask_restful import Resource
from poly.utils.fields import month_field
from poly.reestr.xml.pack.sql_xml import make_xml

class MakeXml(Resource):

    def result(self, filename, message, detail=None):
        return dict(
            file=filename.split('\\')[-1],
            message=message,
            detail=detail
        )
    
    def post(self):

        time1 = datetime.now()

        year, month = month_field( request.form.get('month', '') )
        # pack number
        pack = request.form.get('pack', '01')
        # if sent is None ignore already sent, produce full pack
        sent = request.form.get('sent', None)
        #current_app.logger.debug(year, month, pack, sent)
        try:
            ph, lm, file = make_xml(current_app, year, month, pack, sent)
        except Exception as e:
            current_app.logger.debug(e)
            return self.result('', 'PROCESSING ERROR', detail='see log'), current_app.config['CORS']
        
        time2 = datetime.now()
        msg = f'Сформировано {ph} PHМ записей, {lm} LM записей время: {(time2 - time1)} '

        return self.result(file, msg, detail=None), current_app.config['CORS']

