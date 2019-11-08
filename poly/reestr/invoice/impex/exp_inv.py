
import os
from datetime import date
from pathlib import Path
import psycopg2
import psycopg2.extras
from openpyxl import load_workbook
#from openpyxl.compat import range
from openpyxl.styles import Border, Side, colors
from poly.reestr.invoice.impex import config

def get_mo_smo_name(app, qurs, smo, cfg):
    
    mo_code= app.config['MO_CODE'][0] 
    qurs.execute(cfg.GET_MO_NAME, ( mo_code, ) )
    mq= qurs.fetchone()
    if mq:
        mo_name= mq[0]
    else:
        mo_name= cfg.STUB_MO
    if len(smo) > 0:
        ins= 250000 + int(smo)
        qurs.execute(cfg.GET_SMO_NAME, ( ins, ))
        mq= qurs.fetchone()
        if mq:
            smo_name=  mq[0]
        else:
            smo_name= cfg.STUB_SMO
    else:
        smo_name= ''
    
    return mo_name, smo_name
    

def extract(row):
    d = [ '' for i in range(20)]
    d[0] = row.nhistory
    fam = row.fam or ' '
    im = row.im or ' '
    ot = row.ot or ' '
    d[1] = '%s %s %s' % (row.fam, im[0].upper(), ot[0].upper())  
    d[2] = row.w
    d[3] = row.dr
    #d[4] = ''
    #docser = row.docser or ' '
    #docnum = row.docnum or ' '
    #d[5] = '%s %s' % (docser, docnum)
    #d[6], d[7], d[8] = '', '', '' 
    spolis = row.spolis or ''
    npolis = row.npolis or ''
    d[9] = '%s %s' % (spolis, npolis)
    #''.join(i for i in row.p_num if i.isdigit())
    # re.sub("\D", "", )
    d[10] = row.vidpom
    d[11] = row.ds1
    d[12] = '%s~%s' % (row.date_z_1, row.date_z_2)
    d[13] = 1
    d[14] = row.profil
    d[15] = row.prvs
    d[16] = price = row.sumv
    #d[17] = row.foms_price
    if row.sank_it:
        #price -= row.sank_it
        if price:
            d[5]= 'МЭК'
        else:
            d[5]= 'ХЭК'
        price= 0.00
    d[17] = price 
    
    d[18] = row.rslt
    #d[19] = row.ishod
    
    return d


def for_foms(dex, rc):
    # d - list from extract
    d = ['' for i in range(20)]
    d[0] = rc
    # nusl, fio
    d[1], d[2] = dex[0], dex[1]
    # pol
    #d[3] = ['м', 'ж'].index( dex[2] ) - 1
    d[3]= dex[2]
    # date_birth, place_birth
    d[4], d[5] = dex[3], dex[4]
    # d[6] # document
    # d[7] # snils
    # polis
    d[8] = dex[9]
    # vid_pom
    d[9] = dex[10]
    # DS
    d[10] = dex[11]
    # date
    d[11], d[12] = dex[12].split("~")
    i = 13
    for v in dex [13:]:
        d[ i ] = v
        i += 1

    return d

def exp_inv(app: object, insurer: str, month: str, yar: str, typ: int, inv_path: str, is_calc='' ) -> (int, str):
    
    # insurer: string ( 11, 16 )
    # month: string 01-12
    # typ: 1-5
    # inv_path: string path to
    # is_calc: str if non empty then calculatede reestr
    
    m= int(month)
    
    #if m == 1: m = 2 # same month 
    #m_1 = '{0:02d}'.format( m-1 )
    #m_2 = '{0:02d}'.format( m+1 )
    
    tpl= config.TYPE[typ-1][2]
    _data= config.GET_ROW_INV if len(is_calc) == 0 else config.GET_ROW_MO
    
    qonn= app.config.db()
    qurs = qonn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    
    sh1 = 'Лист1'
    
    xtpl = f'{tpl}.xlsx'
    xlr = os.path.join(inv_path, 'tpl', xtpl)   
    
    mo_name, smo_name = get_mo_smo_name(app, qurs, insurer, config)
    
    xout = f'{tpl}{is_calc}_0{insurer}_{month}-{yar}.xlsx'
    xlw = os.path.join(inv_path, xout)   
    #year = '%s' % date.today().isocalendar()[0]
    #y = year[3]
    year= f'20{yar}'
    period = 'За %s %s года' % (app.config['MONTH'][m-1], year)
    
    wb = load_workbook(filename = xlr)
    wb.active
    sheet = wb[sh1]
    if insurer == '':
        sheet['C4'].value = period
        # begin from 17 string
        cntRowXls = 17
    else:
        sheet['E2'].value = '%s ОГРН %s' % (mo_name, app.config['OGRN'])
        sheet['E7'].value = smo_name
        sheet['J1'].value = period
        # begin from 13 string
        cntRowXls = 13

    border = Border(
        left=Side(border_style='thin', color=colors.BLACK),
        right=Side(border_style='thin', color=colors.BLACK),
        top=Side(border_style='thin', color=colors.BLACK),
        bottom=Side(border_style='thin', color=colors.BLACK)
    )    

    rcTotal = 1
    irang=20 # 20 cells in row
    #irang=21 # 21 cells in row
    qurs.execute(_data)
    dc= 0
    for row in qurs.fetchall():
        data = extract(row)
        if insurer == '':
            data = for_foms(data, rcTotal)

        for xrow in range(cntRowXls, cntRowXls+1):
            for xcol in range(1, irang):
                try:
                    c = sheet.cell(column=xcol, row=xrow, value= data[ xcol-1 ])
                    c.border = border
                except Exception as e:
                    app.logger.debug('\n row %s ' % rcTotal)
                    app.logger.debug(data)
                    raise e
            cntRowXls += 1   
            #dc += 1
            #if dc > 250:
            #   print('-- %s --' % rcTotal, end='\r')
            #    dc = 0
            rcTotal += 1
        
    wb.save(xlw)
    wb.close()
    qurs.close()
    qonn.close()
    
    return (rcTotal-1, xlw)
