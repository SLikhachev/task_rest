import os
from datetime import datetime
#from pathlib import Path
from flask import request, current_app, g
from werkzeug import secure_filename
from poly.reestr.task import RestTask
from poly.reestr.xml.vmx.vmx_sql import to_sql
from poly.utils.fields import month_field
from poly.utils.files import allowed_file
from poly.reestr.invoice.mek import config

class MoveMek(RestTask):

    def __init__(self):
        super().__init__()
        self.task= 'move_mek'

    def this_error(self, file):
        return self.close_task(file, 'Ошибка обработки (подробно в журнале)', False)

    # move to next month task
    def post(self):

        ts = self.open_task()
        if len(ts) > 0:
            return self.busy(ts)

        self.pack_type= request.form.get('type', 1)

        files= request.files.get('file', None)
        if not bool(files):
            return self.close_task( '', 'Передан пустой запрос на обработку', False)
        
        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reestr', 'vmx')   
        filename = secure_filename(files.filename)
        if not allowed_file( files.filename, current_app.config ) or not filename.endswith('.xml'):
            return self.close_task(filename, "Допустимое расширение имени файла .xml", False)

        lpu, self.smo, ar, self.month = self.parse_xml_name(filename)
        self.year = f'20{ar}'

        # save file to disk
        up_file = os.path.join(catalog, filename)
        files.save(up_file)
        rc= wc= errors= 0
        try:
            rc= to_sql(up_file, ar, ('824',), 'ignore')
        except Exception as e:
            self.abort_task()
            raise e
            current_app.logger.debug(e)
            return self.this_error(filename)

        msg = f'VM файл {filename} Записей считано {rc}. {self.perf()}'
        os.remove(up_file)
        #files.close()

        return self.close_task(filename, msg, True)

    # export to csv task
    def get(self):
        
        # ints
        year, month = month_field( request.args.get('month', '') )
        month_str= current_app.config['MONTH'][month-1]
        
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
        filename= f"MEK_{df}.csv"
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
