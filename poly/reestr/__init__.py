from flask import Blueprint
from flask_restful import Api

bp = Blueprint('reestr', __name__, url_prefix='/reestr')
api = Api(bp)

# import dbf file
#from poly.reestr.imp.dbf import task as imp_dbf
#api.add_resource(imp_dbf.ImportDbf, '/import/dbf', endpoint='imp_dbf')

# make xml pack
from poly.reestr.xml.pack import task as xml_pack
api.add_resource(xml_pack.MakeXml, '/xml/pack', endpoint='xml_pack')

# parce xml errors file
from poly.reestr.xml.errs import task as xml_errs
api.add_resource(xml_errs.ErrsXml, '/xml/errf', endpoint='xml_errs')

# import/export BARS invoice
from poly.reestr.invoice.impex import task as inv_impex
api.add_resource(inv_impex.InvImpex, '/inv/impex', endpoint='inv_impex')

# calculate reestr ourselves
from poly.reestr.invoice.calc import task as inv_calc
api.add_resource(inv_calc.InvCalc, '/inv/calc', endpoint='inv_calc')

# export/move MEK records
from poly.reestr.invoice.mek import task as move_mek
api.add_resource(move_mek.MoveMek, '/inv/mek', endpoint='inv_mek')
