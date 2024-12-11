from flask import Blueprint
from flask_restful import Api

bp = Blueprint('clinic', __name__, url_prefix='/clinic/')
api = Api(bp)

from poly.clinic import views # noqa: E402
api.add_resource(views.Hello, 'hello')
#import poly.clinic.views