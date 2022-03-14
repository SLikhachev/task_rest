
import types
import psycopg2
import psycopg2.extras
from poly.reestr.invoice.impex import config as imp_conf
from poly.reestr.invoice.calc import config
from poly.reestr.invoice.tarif.tarif_class import Tarif

sn = types.SimpleNamespace()

def vidpom(row):
    if row.profil in (78, 82):
        return 11
    if row.prvs in (76, ) and row.profil in (97, 160):
        return 12
    return 13

def idsp(row):
    # as pavlenkov
    if row.for_pom == 2:
        return 29
    if row.profil in config.STOM:
        if row.smo == 0:
            if (row.visit_pol + row.visit.home) == 1:
                return 29
            return 30
        return 28
    if row.purp in config.PROF or ( row.smo == 0 and row.profil in config.SESTRY ):
        return 28
    if row.usl_ok == 2:
        return 33
    if (row.visit_pol + row.visit_home) == 1:
            return 29
    return 30

def gender(gen):
    try:
        return ['м', 'ж'].index(gen) + 1
    except:
        return 1

def calc_row(row: tuple):#  -> tuple:
    global sn
    # row: NamedTuple
    tarif, summa, event = sn.sTarif.set_data(row).process()
    mek= 1.00 if row.mek else 0.00
    return (
        row.n_zap, row.id_pac, row.spolis, row.npolis,
        row.usl_ok, vidpom(row), row.for_pom,
        row.date_z_1, row.date_z_2, row.rslt, row.ishod,
        row.profil, row.nhistory, row.ds1, row.prvs, idsp(row),
        summa, mek,
        row.fam, row.im, row.ot, gender(row.w), row.dr
    )

def calc_inv(app: object, sql: object, smo: int, month: str, year: str, typ: int): # -> tuple:
    # app - flask app
    global sn
    print(smo)
    #global sn
    # only one allowed yet
    if typ-1 > 0:
        return (1, False)

    qurs = sql.db.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    qurs1 = sql.db.cursor()
    sql.init_db(qurs1)
    qurs1.execute(imp_conf.TRUNC_TBL_MO)
    sql.db.commit()
    lpu_code = app.config.get('LPU_CODE', ()) # sort code
    sn.sTarif= Tarif(sql.db, lpu_code, year )

    # 2. process table
    # ---------------------------------------------
    ya= int(year[2:])
    #so = int(smo) + 25000
    qurs.execute(config.GET_SMO_AMBUL, ( ya, month, smo ))
    rc= 0
    for row in qurs.fetchall():
        res= calc_row(row)
        qurs1.execute(imp_conf.INS_MO, res)
        rc += 1

    sql.db.commit()
    #qurs1.execute(imp_conf.COUNT_MO)
    #rc= qurs.fetchone()

    qurs.close()
    qurs1.close()

    return ( rc, True )
