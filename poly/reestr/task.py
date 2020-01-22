
from time import perf_counter
from flask import g, current_app
from flask_restful import Resource

class RestTask(Resource):
    
    # YAR field for current task running
    def open_task(self, flag):
        self.mo_code = current_app.config['MO_CODE'][0]
        g.qonn = current_app.config.db()
        self.qurs = g.qonn.cursor()
        # check if task is running
        #self.qurs.execute(config.GET_INV_TASK, (self.mo_code,))
        
        self.qurs.execute(self.get_task, (self.mo_code,))
        task = self.qurs.fetchone()
        if task is None:
            return 'Нет записей в таблице задач'
        if len(task) and bool(task[0]):
            self.qurs.close()
            return 'Расчет уже запущен'
        self.qurs.execute(self.set_task, (flag, self.mo_code))
        g.qonn.commit()
        self.time1= perf_counter()
        return ''

    def perf(self):
        return f'Время: {round( (perf_counter() - self.time1), 2)}'

    def close_task(self, file, msg, done, abort=''):
        self.qurs.execute(self.set_task, (0, self.mo_code))
        g.qonn.commit()
        self.qurs.close()
        if abort:
            return None
        return self.out(file, msg, done)

    def abort_task(self):
        return self.close_task('', '', False, 'abort')

    def result(self, filename, message, done=False):
        if 'qonn' in g:
            g.qonn.close()
        if bool(filename) and len(filename) > 0:
            file = filename.split('\\')[-1]
        else:
            file= ''
        return dict(
            file=file,
            message=message,
            done=done
        )

    def out(self, file, msg, done):
        return self.result(file, msg, done), current_app.config['CORS']