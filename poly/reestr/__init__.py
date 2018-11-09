from flask import Blueprint
from flask_restful import Api

bp = Blueprint('report', __name__, url_prefix='/reestr')
api = Api(bp)

from poly.reestr.imp.reestr import task as imp_reestr
api.add_resource(imp_reestr.ImportReestr, '/import/reestr', endpoint='imp_reestr')

