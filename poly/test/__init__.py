from flask import Blueprint
from flask_restful import Api

bp = Blueprint('test', __name__, url_prefix='/test')
api = Api(bp)

from poly.test import task as test_task
api.add_resource(test_task.TestTask, '', endpoint='test_task')


