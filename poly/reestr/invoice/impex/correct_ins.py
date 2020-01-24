
import psycopg2
import psycopg2.extras
from flask import g
from poly.reestr.invoice.impex import config


def correct_ins(smo: int, month: str, year: str) -> int:
    # smo: int ( 25011, 25016 )
    
    qurs = g.qonn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    qurs1= g.qonn.cursor()
    #ismo= int(smo) + 25000
    imon= int(month)
    ar= year[2:]
    #tal= config.GET_SMO % year
    #get_smo= f'{tal}%s{config.AND_CRD}'
    #qurs1.execute(config.GET_ROW_INV_TAL)

    get_recs= config.GET_INV_SMO % (ar, imon, smo)
    qurs.execute(get_recs)
    dc= 0
    # dont USE this error 
    for row in qurs.fetchall():
        '''   
        tal_num= row[0]
        qurs.execute(get_smo, (tal_num,)) # crd_num, smo
        tal= qurs.fetchone()
        if tal is None:
            continue
        tsmo= int(tal.smo)
        if tsmo == ismo:
            continue
     '''
        qurs1.execute(config.UPDATE_TAL_SMO, (ar, smo, row.tal_num ))
        qurs1.execute(config.UPDATE_CRD_SMO, (smo, row.crd_num ))
        dc += 1
        
    g.qonn.commit()
    qurs.close()
    qurs1.close()
    
    return (dc,)
