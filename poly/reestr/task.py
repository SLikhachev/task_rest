
from time import perf_counter
from flask import g, current_app
from flask_restful import Resource

GET_TASK='SELECT running FROM task_rest WHERE task= %s;'
RUN_TASK='UPDATE task_rest SET running=1 WHERE  task =%s;'
#STOP_TASK= 'UPDATE task_rest SET running=0 WHERE  task =%s;'

STOP_TASK='''
UPDATE task_rest SET running=0, task_year=%s, task_month=%s, smo=%s, pack_num=%s, pack_type=%s
WHERE task=%s;
 '''


class RestTask(Resource):

    def __init__(self):
        super().__init__()
        self.year= None
        self.month= None
        self.smo= None
        self.pack_num= None
        self.pack_type= None

    def open_task(self):
        g.qonn = current_app.config.db()
        self.qurs = g.qonn.cursor()

        # check if task is running
        self.qurs.execute(GET_TASK, (self.task,))
        tsk = self.qurs.fetchone()
        if tsk is None:
            return 'Нет такой задачи в таблице задач'
        if len(tsk) and bool(tsk[0]):
            self.qurs.close()
            return 'Задача уже запущена'
        self.qurs.execute(RUN_TASK, (self.task,))
        g.qonn.commit()
        self.time1= perf_counter()
        return ''

    def perf(self):
        return f'Время: {round( (perf_counter() - self.time1), 2)}'

    def close_task(self, file, msg, done, abort=''):
        self.qurs.execute(STOP_TASK,
            (self.year, self.month, self.smo, self.pack_num, self.pack_type, self.task))
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

    def busy(self, msg):
        return self.out('', msg, False)
