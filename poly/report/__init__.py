from flask import Blueprint
from flask_restful import Api

bp = Blueprint('report', __name__, url_prefix='/report')
api = Api(bp)

from poly.report.common.hosp import task as hosp_task
#api.add_resource(hosp_task.TakeCsv, '/common/hosp/take_csv', endpoint='take_csv')
api.add_resource(hosp_task.MakeReport, '/common/hosp/make_report', endpoint='make_report')
#import poly.clinic.views