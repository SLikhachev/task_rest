
from flask import g
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
