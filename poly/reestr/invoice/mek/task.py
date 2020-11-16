
import os
from datetime import datetime
from flask import request, current_app, g
from poly.reestr.task import RestTask
from poly.utils.fields import month_field
from poly.utils.files import get_name_tail
from poly.reestr.invoice.mek import config
from poly.reestr.invoice.mek.move_mek import move_mek

class MoveMek(RestTask):

    def __init__(self):
        super().__init__()
        self.task= 'move_mek'

    def month_str(self, m, y):
        return  f'{current_app.config["MONTH"][m-1]} {y}'

    def this_error(self, file):
        return self.close_task(file, 'Ошибка обработки (подробно в журнале)', False)

    # move to next month task
    def post(self):

        ts = self.open_task()
        if len(ts) > 0:
            return self.busy(ts)
        
        self.year, self.month = month_field( request.form.get('month', '') )
        _, self.target_month = month_field( request.form.get('target', '') )
        
        if self.this_year != self.year:
            return self.close_task('', f'Переносить МЭК можно только в текущем году', False)
        if self.target_month <= self.month:
            return self.close_task('', f'Переносить МЭК можно только вперед', False)
        
        #return self.close_task('', 'Done', True)
        
        try:
            rc= move_mek(self.this_year, self.month, self.target_month)
        except Exception as e:
            #self.abort_task()
            raise e
            current_app.logger.debug(e)
            return self.this_error(filename)
        
        if not bool(rc):
            month_str= self.month_str(self.month, self.year)
            return self.close_task('', f'Нет МЭКов за {month_str}', False)
        
        month_str= self.month_str(self.target_month, self.year)
        msg = f'Пернесли МЭКи на {month_str} записей {rc}.'
       
        return self.close_task('', msg, True)

    # export to csv task
    def get(self):
        
        # ints
        year, month = month_field( request.args.get('month', '') )
        month_str= self.month_str(month, year)
        
        g.qonn= current_app.config.db()
        qurs= g.qonn.cursor()
        ar= year - 2000
        qurs.execute(config.COUNT_MEK, (ar, month ))
        mc= qurs.fetchone()

        if (mc is None) or mc[0] == 0:
            qurs.close()
            return self.out('',
              f'Нет записей с МЭК за {month_str} месяц', True)
        
        mc= mc[0]
        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reestr', 'mek')
        df= str(datetime.now()).split(' ')[0]
        filename= f"MEK_{df}_{get_name_tail(4)}.csv"
        up_file = os.path.join(catalog, filename)
        
        _q= config.MEK_FILE % up_file  
       
        _q = f'{config.TO_CSV}{_q}'  
        try:
           qurs.execute(_q, (ar, month))
        except Exception as e:
            qurs.close()
            g.qonn.close()
            raise e
            current_app.logger.debug(e)
            return self.this_error(filename)
        
        qurs.close()
        return self.out(up_file,  f"МЭК за {month_str} месяц, записей в файле {mc}", True)
