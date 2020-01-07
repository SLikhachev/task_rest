
from flask import g, current_app
from flask_restful import Resource

class RestTask(Resource):

    def open_task(self, flag):
        self.mo_code = current_app.config['MO_CODE'][0]
        g.qonn = current_app.config.db()
        self.qurs = g.qonn.cursor()
        # check if task is running
        #self.qurs.execute(config.GET_INV_TASK, (self.mo_code,))
        self.qurs.execute(self.get_task, (self.mo_code,))
        task = self.qurs.fetchone()
        if len(task) and task[0] > 0:
            self.qurs.close()
            return True
        self.qurs.execute(self.set_task, (flag, self.mo_code))
        g.qonn.commit()
        return False

    def close_task(self, file, msg, done):
        self.qurs.execute(self.set_task, (0, self.mo_code))
        g.qonn.commit()
        self.qurs.close()
        return self.out(file, msg, done)

    def result(self, filename, message, done=False):
        if 'qonn' in g:
            g.qonn.close()
        return dict(
            file=filename.split('\\')[-1],
            message=message,
            done=done
        )

    def out(self, file, msg, done):
        return self.result(file, msg, done), current_app.config['CORS']