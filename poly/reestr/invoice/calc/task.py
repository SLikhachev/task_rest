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

    def __init__(self):
        super().__init__()
        self.task= 'self_calc'

    def post(self):

        ts = self.open_task()
        if len(ts) > 0:
            return self.busy(ts)

        self.pack_type= int( request.form.get('type', 1) )
        smo= request.form.get('smo', '')
        self.year, self.month = month_field( request.form.get('month', '') )
        self.smo = int(smo) if smo else 0

        wc= 0
        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reestr', 'calc')

        #test
        #msg= f' type={typ} smo={smo} year={yar} month={mon}'
        #return self.close_task('', msg, False)

        try:
            # PMU
            if self.pack_type == 6:
                return self.close_task('', 'Расчет не реализован', False)

            rc, res = calc_inv(current_app, self.year, self.month, self.smo, self.pack_type)
            if  not res:
                current_app.logger.debug(config.FAIL[rc])
                return self.close_task('', config.FAIL[rc], False)
            wc, xreestr = exp_inv(
                current_app, self.smo, self.month, self.year, self.pack_type, catalog, '_calc')

        except Exception as e:
            self.abort_task()
            raise e
            current_app.logger.debug(e)
            msg= f'Ошибка обработки {e}'
            return self.close_task('', msg, False)
        
        msg = f'Счет {config.TYPE[self.pack_type-1][1]} Записей обработано {wc}. {self.perf()}'
                
        return self.close_task(xreestr, msg, True)
