import sys
import pyodbc
import psycopg2
#from datetime import date
from poly.reestr.imp.dbf import config


def dbf_to_sql (app, dbf_dir, dbf_file, month, year, test):
        
    #r = f'{dbf_dir} {dbf_file} {month} {year} {test}'
    #app.logger.debug(r)
    
    # app current_app obj
    # dbf_dir string - file upload dir
    # dbf_file string - file upload name
    # db db connection obj
    # month - month int
    # year - year int
    # test - bool test if True

    par = "Driver={Microsoft dBASE Driver (*.dbf)};DefaultDir=%s" % dbf_dir

    god, rn = '%s' % year,  dbf_file[:2].upper()
    if month > 9:
        ms = f'{month}'
    else:
        ms = f'0{month}'
    
    if rn not in config.TNAME:

        return (0, 0, 1, 'Неизвестное имя файла')
    
    if dbf_file[2:5] not in app.config['MO_CODE']:
        return 0, 0, 1, 'Неизвестный код МО'

    if dbf_file[5] != god[-1]:
        return 0, 0, 1,  'Неврная цифра года'

    if dbf_file[6:8] != ms:
        return 0, 0, 1, 'Неврный месяц'

    create_tbl = eval('config.CREATE_%s' % rn)
    _tb = '_%s_%s_%s' % (dbf_file[2:5], ms, god[2:])
    table = f'{rn}{_tb}'


    dbf = pyodbc.connect(par, autocommit=True)
    curs = dbf.cursor()
    select_dbf = 'SELECT * FROM %s'

    db = psycopg2.connect(app.config['DB_CONF'])
    qurs = db.cursor()
    if not test:
        qurs.execute(create_tbl % _tb)
        qurs.execute(config.TRUNCATE % table)
        db.commit()

    if rn != 'RR' and not test:
        create_ind = eval('config.CREATE_IND_%s' % rn)
        qurs.execute(create_ind % (_tb, _tb))
        db.commit()

    rc, wc, err = 0, 0, 0
    int_ind = eval('config.%s_INT' % rn)
    float_ind = eval('config.%s_FLOAT' % rn)
    insert = config.INSERT % table

    for r in curs.execute(select_dbf % dbf_file):
        wc += 1
        vv = ['default']
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

        vals = '%s%s%s' % (insert, ' , '.join(vv), ')')
        #print(vals)
        # break
        try:
            if not test:
                qurs.execute(vals)
                db.commit()
                rc += qurs.rowcount
            else:
                rc += 1
        except Exception as e:
            err += 1
            app.logger.debug( 'Err: %s' % e)
            if not test:
                db.rollback()
            #break    

    db.commit()
    qurs.close()
    db.close()

    curs.close()
    dbf.close()
    msg = ''
    if err > 0:
        msg += 'Ошибки БД'
    return rc, wc, err, msg
