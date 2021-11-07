
from poly.reestr.invoice.mek import config


def move_mek(db: object, year: str, month: str, target_month: str) -> int:
    
    qurs= db.cursor()
    source_mon= int(month)
    target_mon = int(target_month)
    ar= year[2:]
    
    qurs.execute(config.COUNT_MEK, (ar, month ))
    mc= qurs.fetchone()
    if (mc is None) or mc[0] == 0:
        qurs.close()
        return 0
    
    move_mek= config.MOVE_MEK % (ar, target_mon, source_mon)
    qurs.execute(move_mek)
    db.commit()
    rc= qurs.rowcount
   
    qurs.close()
    
    return rc
