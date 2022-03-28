
from psycopg2 import sql
import xml.etree.cElementTree as ET
from poly.reestr.invoice.impex import config
from poly.reestr.invoice.impex.utils import get_text, tmp_table_name


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

def imp_usl(hm: str, _sql: object): # -> tuple:
    global rec
    usld= dict()

    context = ET.iterparse(hm)
    for _, elem in context:
        if elem.tag == 'USL':
            ud= proc(elem)
            #app.logger.debug(ud)
            if usld.get( ud['CODE_USL'], None ) is None:
                usld[ ud['CODE_USL'] ]= [ ud[ t ] for t in rec]
            else:
                usld[ ud['CODE_USL'] ][0] += ud['KOL_USL']

    usl_table = tmp_table_name()
    create= sql.SQL(config.CREATE_TBL_USL).format(usl_table)
    _sql.qurs.execute(create)
    _sql._db.commit()

    for k in usld.keys():
        try:
            r= [k]
            r.extend ( usld[k] )
            _sql.qurs.execute(sql.SQL(config.INS_USL_TMP).format(usl_table), r)
        except Exception as e:
            raise e

        _sql._db.commit()

    _sql.qurs.execute(sql.SQL(config.COUNT_USL_TMP).format(usl_table))
    rc= _sql.qurs.fetchone()

    #qurs.close()
    setattr(_sql, 'usl_table', usl_table)
    # return signature ( ( rows_of_imported, rows_of_corrected ), done_status)
    return ( (rc[0], 0), True) if bool(rc) and len(rc) > 0 else ( (2, 0), False)
