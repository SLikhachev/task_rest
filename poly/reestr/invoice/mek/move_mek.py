
from poly.reestr.invoice.mek import config


def move_mek(sql: object, year: int, source_month: int, target_month: int): # -> int:

    qurs= sql.db.cursor()
    sql.init_db(qurs)
    ar= year - 2000

    qurs.execute(config.COUNT_MEK, (ar, source_month ))
    mc= qurs.fetchone()
    if (mc is None) or mc[0] == 0:
        qurs.close()
        return 0

    q = config.MOVE_MEK % (ar, target_month, source_month)
    qurs.execute(q)
    sql.db.commit()
    rc= qurs.rowcount

    qurs.close()

    return rc
