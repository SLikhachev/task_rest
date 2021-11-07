
import xml.etree.cElementTree as ET
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
    
def imp_usl(hm: str, db: object) -> tuple:
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
    
            

    qurs = db.cursor()
    qurs.execute(config.TRUNC_TBL_USL)
    db.commit()
    
    for k in usld.keys():
        try:
            r= [k]
            r.extend ( usld[k] )
            qurs.execute(config.INS_USL, r )
        except Exception as e:
            raise e
    
        db.commit()
    
    qurs.execute(config.COUNT_USL)
    rc= qurs.fetchone()
    
    qurs.close()
    
    # return signature ( ( rows_of_imported, rows_of_corrected ), done_status)
    return ( (rc[0], 0), True) if bool(rc) and len(rc) > 0 else ( (2, 0), False)
