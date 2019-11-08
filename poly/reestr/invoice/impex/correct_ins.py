
import psycopg2
import psycopg2.extras
from poly.reestr.invoice.impex import config


def correct_ins(app: object, smo: str) -> int:
    # insurer: string ( 11, 16 )
    
    qonn= app.config.db()
    qurs = qonn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    qurs1= qonn.cursor()
    
    qurs1.execute(config.GET_ROW_INV_TAL)
    dc= 0
    # dont USE this error 
    for row in qurs1.fetchall():
        tal_num= row[0]
        tal_smo= int(smo)
        crd_smo= tal_smo + 25000
        qurs.execute(config.GET_TALON, (tal_num,))
        tal= qurs.fetchone()
        if tal is None:
            continue
        if tal.smo == tal_smo:
            continue
        qurs.execute(config.UPDATE_TAL_SMO, (tal_smo, tal_num ))
        qurs.execute(config.UPDATE_CRD_SMO, (crd_smo, tal.crd_num ))
        dc += 1
        
    qonn.commit()
    qurs.close()
    qurs1.close()
    qonn.close()
    
    return (dc,)
