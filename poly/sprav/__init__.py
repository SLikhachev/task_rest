from flask import Blueprint
from flask_restful import Api

bp = Blueprint('sparv', __name__, url_prefix='/sprav/')
api = Api(bp)

from poly.sprav import views
api.add_resource(views.Hello, 'hello')
