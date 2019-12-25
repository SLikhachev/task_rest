import os
from datetime import datetime
from pathlib import Path
from flask import request, current_app, Response, g
from poly.reestr.common import RestTask
from poly.utils.fields import month_field
from poly.reestr.invoice.calc.calc_inv import calc_inv
#from poly.reestr.invoice.calc.calc_pmu import calc_pmu
from poly.reestr.invoice.impex.exp_inv import exp_inv
from poly.reestr.invoice.impex import config

class InvCalc(RestTask):

    def post(self):

        time1 = datetime.now()
        typ= int( request.form.get('type', 1) )
        smo= request.form.get('smo', '')
        yar, mon = month_field( request.form.get('month', '') )
        rc= wc= errors= 0
        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reestr', 'inv')   
        err_msg= 'Расчет не реализован'
        # PMU
        if typ == 6:
            return self.result('',err_msg, False), current_app.config['CORS']

        # reestr NOT IMPLEMENTED YET calc_inv returns (-1,)  
        try: 
            wc,  xreestr= exp_inv(current_app, smo, str(mon), str(yar), typ, catalog, '_calc')
        except Exception as e:
            raise e
            current_app.logger.debug(e)
            return self.result('', err_msg, False), current_app.config['CORS']
        
        time2 = datetime.now()
        msg = f'Счет {config.TYPE[typ-1][1]} Записей в счете {rc}, записей в реестре {wc}. Время: {(time2-time1)}'
                
        return self.result(xreestr, msg, True), current_app.config['CORS']
