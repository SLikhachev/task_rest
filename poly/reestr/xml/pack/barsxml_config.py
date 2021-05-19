
import os
from barsxml.path.thispath import Path
from barsxml.config.pgxml import *
from flask import current_app

MO_CODE = current_app.config['MO_CODE'][0]
xmldir = Path(os.path.join(current_app.config['UPLOAD_FOLDER']))
BASE_XML_DIR = xmldir / 'reestr' 

DS = dict(
    p_per = 1,
    podr = 971,
    profil_k= 71
)

KSG = dict(
    ver_ksg = "2021",
    ksg_pg = 1,
    koef_z = 1,
    koef_up = 1,
    bztsz =  13308.72,
    koef_d = 1.369,
    koef_u = 0.8,
    sl_k = 0,
)
