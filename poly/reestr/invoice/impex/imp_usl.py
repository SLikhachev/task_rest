
#import sys, os, types
from decimal import Decimal
import xml.etree.cElementTree as ET
#from datetime import datetime
from flask import g
from poly.reestr.invoice.impex import config
from poly.reestr.invoice.impex.utils import get_text

def kusl(k):
    return int(k.split('.')[0])

usl= ( ('PROFIL', int), ('CODE_USL', str), ('KOL_USL', kusl), ('TARIF', str), ('PRVS', int) )
rec= ('KOL_USL', 'TARIF', 'PROFIL', 'PRVS', )

def proc(el):
    global usl
    u= dict()
    for tag, fn in usl:
        try:
             u[tag]= u[tag]= fn( get_text(el, tag) )
        except:
             u[tag]= None
    return u
    
def imp_usl(hm: str) -> int:
    global rec    
    usld= dict()
    
    context = ET.iterparse(hm)
    for event, elem in context:
        if elem.tag == 'USL':
            ud= proc(elem)
            #app.logger.debug(ud)
            if usld.get( ud['CODE_USL'], None ) is None:
                usld[ ud['CODE_USL'] ]= [ ud[ t ] for t in rec]
            else:
                usld[ ud['CODE_USL'] ][0] += ud['KOL_USL'] 
    
            
    #qonn = app.config.db()
    qurs = g.qonn.cursor()
    qurs.execute(config.TRUNC_TBL_USL)
    #qurs.execute(config.CREATE_TBL_USL)
    g.qonn.commit()
    
    for k in usld.keys():
        try:
            r= [k]
            #t= [ i for i in usld[k] ]
            r.extend ( usld[k] )
            qurs.execute(config.INS_USL, r )
        except Exception as e:
            raise e
    
    g.qonn.commit()
    
    qurs.execute(config.COUNT_USL)
    rc= qurs.fetchone()
    
    qurs.close()

    return (rc[0], True) if bool(rc) and len(rc) > 0 else (2, False)
