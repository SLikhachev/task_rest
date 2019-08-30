from flask import Blueprint
from flask_restful import Api

bp = Blueprint('reestr', __name__, url_prefix='/reestr')
api = Api(bp)

# import dbf file
from poly.reestr.imp.dbf import task as imp_dbf
api.add_resource(imp_dbf.ImportDbf, '/import/dbf', endpoint='imp_dbf')

# make xml pack
from poly.reestr.xml.pack import task as xml_pack
api.add_resource(xml_pack.MakeXml, '/xml/pack', endpoint='xml_pack')

# parce vmxml pack
from poly.reestr.xml.vmx import task as vmx_pars
api.add_resource(vmx_pars.XmlVmx, '/xml/vmx', endpoint='vmx_pars')