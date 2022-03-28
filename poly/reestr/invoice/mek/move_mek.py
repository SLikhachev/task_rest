
from poly.reestr.invoice.mek import config


def move_mek(_sql: object, year: int, source_month: int, target_month: int): # -> int:

    #qurs= sql.db.cursor()
    #sql.init_db(qurs)
    ar= year - 2000

    _sql.qurs.execute(config.COUNT_MEK, (ar, source_month ))
    mc= _sql.qurs.fetchone()
    if (mc is None) or mc[0] == 0:
        #qurs.close()
        return 0

    q = config.MOVE_MEK % (ar, target_month, source_month)
    _sql.qurs.execute(q)
    _sql._db.commit()
    rc= _sql.qurs.rowcount

    #qurs.close()

    return rc
