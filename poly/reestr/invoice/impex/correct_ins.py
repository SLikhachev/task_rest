
import psycopg2
import psycopg2.extras
from flask import g
from poly.reestr.invoice.impex import config


def correct_ins(smo: str, year: str) -> int:
    # smo: string ( 11, 16 )
    
    qurs = g.qonn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    qurs1= g.qonn.cursor()
    ismo= int(smo) + 25000
    tal= config.GET_SMO % year
    get_smo= f'{tal}%s{config.AND_CRD}'
    qurs1.execute(config.GET_ROW_INV_TAL)
    dc= 0
    # dont USE this error 
    for row in qurs1.fetchall():
        tal_num= row[0]
        qurs.execute(get_smo, (tal_num,)) # crd_num, smo
        tal= qurs.fetchone()
        if tal is None:
            continue
        tsmo= int(tal.smo)
        if tsmo == ismo:
            continue
        qurs.execute(config.UPDATE_TAL_SMO, (year, tsmo, tal_num ))
        qurs.execute(config.UPDATE_CRD_SMO, (tsmo, tal.crd_num ))
        dc += 1
        
    g.qonn.commit()
    qurs.close()
    qurs1.close()
    
    return (dc,)
