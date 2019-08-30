#import sys
#import pyodbc
#import datetime
#import json
import psycopg2
import psycopg2.extras
import xml.etree.cElementTree as ET
from poly.reestr.xml.vmx import config

"""
 <?xml version="1.0" encoding="utf-8" ?> 
- <FLK_P>
    <FNAME>VM250228T25_19072285.xml</FNAME> 
    <FNAME_I>HM250228T25_19072285.xml</FNAME_I> 
-   <SCHET>
        <CODE>2281908</CODE> 
        <CODE_MO>250228</CODE_MO> 
        <YEAR>2019</YEAR> 
        <MONTH>7</MONTH> 
        <NSCHET>228190801</NSCHET> 
        <DSCHET>2019-07-31</DSCHET> 
    </SCHET>
-   <ZAP>
        <N_ZAP>55665</N_ZAP> 
-       <SL>
            <SL_ID>1</SL_ID> 
            <IDCASE>55665</IDCASE> 
            <NHISTORY>55665</NHISTORY> 
            <CARD /> 
            <SMO>25016</SMO> 
            <SMO_FOND>25016</SMO_FOND> 
-           <OTKAZ>
                <I_TYPE>910</I_TYPE> 
                <COMMENT>-1 - Нет информации о страхованиях в ЦС ЕРЗ ОМС!</COMMENT> 
            </OTKAZ>
-           <OTKAZ>
                <I_TYPE>910</I_TYPE> 
                <COMMENT /> 
            </OTKAZ>
-           <OTKAZ>
                <I_TYPE>903</I_TYPE> 
                <COMMENT /> 
            </OTKAZ>
        </SL>
    </ZAP>
"""

def process(zap, ignore, errors='ignore'):
    
    ite= []
    res= []
    sl = zap.find('SL')
    card = sl.find('CARD').text
    idcase = int( sl.find('IDCASE').text) 
    for ot in sl.findall('OTKAZ'):
        err = int(ot.find('I_TYPE').text)
        if errors == 'ignore' and err in ignore:
            continue
        if errors == 'select' and err not in ignore:
            continue
        if err in ite:
            continue
        ite.append(err)
        cmt= ot.find('COMMENT').text
        ite.append( err )
        res.append( ( idcase, card, err, cmt ) )
     
    if res == []:
        return None

    return res # list of tuples
"""
tal_num int,
open_date date,
close_date date,
crd_num varchar(20),
fam varchar(40),
error int,
cmt text
"""

talon= config.GET_TALON % ('talonz_clin', 'cardz_clin') + config.TAL

def get_talon(qurs, tal_num):
    global talon
    qurs.execute(talon, (tal_num,))
    return qurs.fetchone()

def write_error(qurs, res):
    tal = get_talon(qurs, res[0][0] )
    if not tal:
        return None
    for err in res:
        qurs.execute( config.WRITE_ERROR,
            ( tal.tal_num,  tal.open_date, tal.close_date, tal.crd_num, tal.fam, err[2], err[3])
        )
    return tal

def to_sql(current_app, file, ignore, errors='ignore'):
    
    qonn = current_app.config.db()
    qurs = qonn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    qurs.execute(config.TRUNCATE_ERROR)
    qonn.commit()
    
    context = ET.iterparse(file, events=("start", "end"))
    event, root = next(context)
    root.clear()
    cnt = 0
    for event, elem in context:
        if event == "end" and elem.tag == "ZAP":
            root = elem
            res = process(root, ignore, errors)
            if res is not None:
                r= write_error(qurs, res)
                if res:
                    cnt += 1
            root.clear()
    
    qonn.commit()
    qurs.close()
    qonn.close()
    
    return cnt

