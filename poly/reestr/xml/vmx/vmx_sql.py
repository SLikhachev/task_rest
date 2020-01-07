import types
#import pyodbc
#import datetime
#import json
from collections import namedtuple
import psycopg2
import psycopg2.extras
from flask import g
import xml.etree.cElementTree as ET
from poly.reestr.xml.vmx import config

sn= types.SimpleNamespace(
    Tal=namedtuple('Tal', ('tal_num', 'open_date', 'close_date', 'crd_num', 'fam')),
    Terr= set()
)

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
        err = ot.find('I_TYPE').text # was int
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


def get_talon(qurs, tal_num):
    global sn
    qurs.execute(sn.talon, (tal_num,))
    return qurs.fetchone()

def write_error(qurs, res):
    global sn
    tal = get_talon(qurs, res[0][0])
    if tal is None:
        tal= sn.Tal(res[0][0], None, None, '', 'Талон не найден')
        #return None
    else:
        sn.Terr.add( int(tal.tal_num) )
    for err in res:
        qurs.execute ( config.GET_ERROR_NAME, (err[2], ) )
        enr= qurs.fetchone()
        en= 'Нет описания'
        if enr:
            en= enr[0]
            
        qurs.execute( config.WRITE_ERROR,
            ( tal.tal_num,  tal.open_date, tal.close_date, tal.crd_num, tal.fam, err[2], str(en) )
        )
    return tal

def mark_talons(qurs):
    global sn
    for t in sn.Terr:
        qurs.execute(sn.mark, (t,))
    sn.Terr.clear()    

def to_sql(current_app, file, year, ignore, errors='ignore'):
    
    global sn
    
    #qonn = current_app.config.db()
    qurs = g.qonn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    qurs.execute(config.TRUNCATE_ERROR)
    g.qonn.commit()
    
    tal_tbl= 'talonz_clin_%s' % year
    sn.talon= config.GET_TALON % (tal_tbl, 'cardz_clin') + config.TAL
    sn.mark= config.MARK_TALON % tal_tbl + '%s;'
    
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
                g.qonn.commit()
                cnt += 1
            root.clear()
    
    mark_talons(qurs)
    
    g.qonn.commit()
    qurs.close()

    return cnt

