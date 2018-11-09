import sys
import pyodbc
#from datetime import date
from poly.reestr.imp.reestr import config


def dbf_to_sql(app, rdir, file, db,  mo, month, year, test):

    par = "Driver={Microsoft dBASE Driver (*.dbf)};DefaultDir=%s" % rdir

    dbf = pyodbc.connect(par, autocommit=True)
    curs = dbf.cursor()
    select_dbf = 'SELECT * FROM %s'

    qurs = db.cursor()
    tb_name = file[:2].upper()
    if tb_name not in config.TNAME:
        return False
    y = f'{year}'[2:]
    if month > 10:
        m = f'{month}'
    else:
        m = f'0{month}'

    create_tbl = eval('config.CREATE_%s' % tb_name)
    rname = f'_{mo}_{m}_{y}'
    table = f'{tb_name}{rname}'
    qurs.execute(create_tbl % rname)

    if tb_name != 'RR':
        create_ind = eval('config.CREATE_IND_%s' % tb_name)
        if test:
            
        qurs.execute(create_ind % (rname, rname))
        db.commit()

    qurs.execute(config.TRUNCATE % table)
    db.commit()
    rc = 0
    int_ind = eval('config.%s_INT' % tb_name)
    float_ind = eval('config.%s_FLOAT' % tb_name)

    for r in curs.execute(select_dbf % file):
        vv = []
        for i, v in enumerate(r):
            if v is None:
                vq = 'NULL'
            elif i + 1 in int_ind:
                vq = '%s' % int(v)
            elif i + 1 in float_ind:
                vq = '%.2f' % float(v)
            else:
                vq = "'%s'" % v
            vv.append(vq)

        vals = '%s%s%s' % ((config.INSERT % table), ' , '.join(vv), ')')
        #print(vals)
        # break
        try:
            qurs.execute(vals)
            db.commit()
            rc += qurs.rowcount
            print('-- %s rows %s -- ' % (tb_name, rc), end='\r')
        except Exception as e:
            print(e)
            # print(vals)
            db.rollback()
            # continue

    db.commit()

    qurs.close()
    #db.close()
    curs.close()
    dbf.close()

    return True

