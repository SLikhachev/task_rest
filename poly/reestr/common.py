
from flask import g, current_app
from flask_restful import Resource

class RestTask(Resource):

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