import os
from datetime import datetime
from pathlib import Path
from flask import request, current_app, Response, g
from poly.reestr.task import RestTask
from poly.utils.fields import month_field
from poly.reestr.invoice.calc.calc_inv import calc_inv
#from poly.reestr.invoice.calc.calc_pmu import calc_pmu
from poly.reestr.invoice.impex.exp_inv import exp_inv
from poly.reestr.invoice.impex import config


class InvCalc(RestTask):

    def post(self):
        # here mon field is used
        self.get_task = config.GET_CALC_TASK
        self.set_task = config.SET_CALC_TASK

        time1 = datetime.now()
        typ= int( request.form.get('type', 1) )
        smo= request.form.get('smo', '')
        yar, mon = month_field( request.form.get('month', '') )

        #  MON field as flag
        if self.open_task(mon):
            return self.out('', 'Расчет уже запущен', False)

        wc= 0
        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reestr', 'calc')

        #test
        #msg= f' type={typ} smo={smo} year={yar} month={mon}'
        #return self.close_task('', msg, False)

        try:
            # PMU
            if typ == 6:
                return self.close_task('', 'Расчет не реализован', False)

            res = calc_inv(current_app, yar, mon, smo, typ)
            if len(res) == 1:
                current_app.logger.debug(config.FAIL[abs(res[0])])
                return self.close_task('', config.FAIL[abs(res[0])], False)

            #msg= f'Table filled {res[0]} {res[1]}'
            #return self.close_task('', msg , True)

            wc,  xreestr= exp_inv(current_app, smo, str(mon), str(yar)[2:], typ, catalog, '_calc')
        except Exception as e:
            raise e
            current_app.logger.debug(e)
            msg= f'Ошибка обработки {e}'
            return self.close_task('', msg, False)
        
        time2 = datetime.now()
        msg = f'Счет {config.TYPE[typ-1][1]} Записей обработано {wc}. Время: {(time2-time1)}'
                
        return self.close_task(xreestr, msg, True)
