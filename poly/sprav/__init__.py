from flask import Blueprint
from flask_restful import Api

bp = Blueprint('sparv', __name__, url_prefix='/sprav')
api = Api(bp)

from poly.sprav.test.apps import task as test_task
api.add_resource(test_task.TaskTest, '/test/task', endpoint='test_task')


