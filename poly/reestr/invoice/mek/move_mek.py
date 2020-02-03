
import psycopg2
import psycopg2.extras
from flask import g
from poly.reestr.invoice.mek import config


def move_mek(month: int, year: int) -> int:
    
    qurs= g.qonn.cursor()
    imon= int(month)
    ar= year - 2000
    
    qurs.execute(config.COUNT_MEK, (ar, month ))
    mc= qurs.fetchone()
    if (mc is None) or mc[0] == 0:
        qurs.close()
        return 0
    
    move_mek= config.MOVE_MEK % (ar, imon+1, imon)
    qurs.execute(move_mek)
    g.qonn.commit()
    rc= qurs.rowcount
   
    qurs.close()
    
    return rc
