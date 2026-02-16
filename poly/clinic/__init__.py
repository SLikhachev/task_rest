from flask import Blueprint
from flask_restful import Api

bp = Blueprint('clinic', __name__, url_prefix='/clinic')
api = Api(bp)

# Create new talonz table
from poly.clinic.talons.table import task as talons_table # noqa: E402
api.add_resource(talons_table.CreateTalonsTable, '/talons/add_table', endpoint='add_talons_table')
