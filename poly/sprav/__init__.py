
from flask import Blueprint
from flask_restful import Api

bp = Blueprint('sprav', __name__, url_prefix='/sprav')
api = Api(bp)
# Update tarifs task
# correct pmu tarifs
from poly.sprav.tarif.pmu import task as tarif_pmu # noqa: E402
api.add_resource(tarif_pmu.UpdateTarifs, '/tarifs/update', endpoint='tarifs_update')
