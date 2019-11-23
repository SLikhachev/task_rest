import os
from datetime import datetime
from pathlib import Path
from flask import request, current_app, Response
from flask_restful import Resource
from poly.utils.fields import month_field
from poly.reestr.invoice.calc.calc_inv import calc_inv
from poly.reestr.invoice.calc.calc_pmu import calc_pmu
from poly.reestr.invoice.impex.exp_inv import exp_inv
from poly.reestr.invoice.impex import config

class InvCalc(Resource):

    def result(self, filename, message, done=False):
        return dict(
            file=filename.split('\\')[-1],
            message=message,
            done=done
        )
    
    def post(self):

        time1 = datetime.now()
        typ= int( request.form.get('typ', 1) )
        smo= request.form.get('smo', '')
        yar, mon = month_field( request.form.get('month', '') )
        rc= wc= errors= 0
        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reestr', 'inv')   
        err_msg= 'Ошибка сервера (детали в журнале)'
        # PMU
        if typ == 6:
            try:
                wc, xreestr= calc_pmu(current_app, smo, str(mon), str(yar), typ, catalog)
                if wc == 0:
                    return self.result( '', config.FAIL[ 2 ], False), current_app.config['CORS']
            except Exception as e:
                #raise e
                current_app.logger.debug(e)
                return self.result('',err_msg, False), current_app.config['CORS']
            time2 = datetime.now()
            msg = f'Расчет {config.TYPE[typ-1][1]} Записей в в файле {wc}. Время: {(time2-time1)}'
            return self.result(xreestr, msg, True), current_app.config['CORS']
        
        # reestr NOT IMPLEMENTED YET calc_inv returns (-1,)  
        try: 
            res= calc_inv(current_app, mon, int(smo), typ)
            if len(res) == 1:
                current_app.logger.debug( config.FAIL[ abs( res[0] ) ] )
                return self.result( '', config.FAIL[ abs( res[0] ) ], False), current_app.config['CORS']
            rc= res[0]
            if rc == 0:
                return self.result( '', config.FAIL[ 2 ], False), current_app.config['CORS']
            
            wc,  xreestr= exp_inv(current_app, smo, str(mon), str(yar), typ, catalog, '_calc')
        except Exception as e:
            #raise e
            current_app.logger.debug(e)
            return self.result('', err_msg, False), current_app.config['CORS']
        
        time2 = datetime.now()
        msg = f'Счет {config.TYPE[typ-1][1]} Записей в счете {rc}, записей в реестре {wc}. Время: {(time2-time1)}'
                
        return self.result(xreestr, msg, True), current_app.config['CORS']
