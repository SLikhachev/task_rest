"""
"""
import sys, os, types
import xml.etree.cElementTree as ET
#from datetime import datetime
from pathlib import Path
from zipfile import ZipFile
from flask import g
from poly.reestr.invoice.impex import config
from poly.reestr.invoice.impex.utils import get_text
from poly.reestr.invoice.impex.imp_usl import imp_usl

sn= types.SimpleNamespace(
    zap= ( 
        'n_zap',
        ('pacient', ('id_pac', 'spolis', 'npolis' ),),
        ('z_sl', (
            'usl_ok', 'vidpom', 'for_pom', 'date_z_1', 'date_z_2', 'rslt', 'ishod',
            ('sl', ( 'profil', 'nhistory', 'ds1', 'prvs',)),
            'idsp', 'sumv', 'sank_it', 
        ))
    ),
    
    pers= ( 'id_pac', 'fam', 'im', 'ot', 'w', 'dr'),
    
    zp_tags = ('ZAP', 'PERS',),

    meta= {}
 )

# here may be generator yelding next text chunk
def get_zp(elem: ET.Element, tags: tuple, rec: list) -> None:
    for t in tags:
        if isinstance(t, tuple):
            e= elem.find( t[0].upper() )
            get_zp(e, t[1], rec ) # yeld from get_zp
        else:    
            rec.append( get_text(elem, t.upper()) ) #yeld get_text
            
def set_zp(rec: list, upd: str) -> None:
    global sn
    if upd == 'ZAP':
        sn.qurs.execute(config.INS_INV, rec)
    else:
        # first el is id_pac
        rec.append( rec.pop(0) )        
        sn.qurs.execute(config.PERSQ, rec)

def zp_xml(xml: str, tags: tuple) -> None:
    global sn
    context = ET.iterparse(xml)
    for event, elem in context:
        rec= list()
        #rc += 1
        #print('-- EXPO HM tags %s --' % rc, end='\r')
        if elem.tag not in sn.zp_tags:
            continue
        #et = ET.ElementTree(elem)
        # if generator then for chunk in get_zp: rec.append(chunk)
        get_zp(elem, tags, rec)
        set_zp(rec, elem.tag)

def set_mek(ar):
    # ar - 2 last digits of year
    global sn
    # set mek flag
    sn.qurs.execute(config.GET_MEK_TABLE, ( int(ar),) )
    t= sn.qurs.fetchone()
    if t is None:
        return 0
    mr = 0
    sn.qurs.execute(config.GET_MEK)
    
    set_mek= (config.SET_MEK % ar) + '%s;'
    for row in sn.qurs.fetchall():
        sn.qurs.execute(set_mek, row)
        mr += 1
    g.qonn.commit()
    return mr

def imp_inv(zipfile: str, typ: int, ar: str) -> tuple:
    # zipfile - file to process
    # typ - invoice type
    # ar - 2 last digits of year
    # returns tuple of 1 if any arrors occured else records count and meta info 
    
    global sn
   
    # 1 unpack file
    p= Path(zipfile)
    zipdir= p.parent
    file= p.name
    
    os.chdir(zipdir)
    _hm= ''
    with ZipFile(file) as zfile:
        for nz in zfile.namelist():
            if nz.startswith('HM') or nz.startswith('CM') or nz.startswith('DOM'):
                zfile.extract(nz)
                _hm= nz
                c= nz[0]
                if c in('H', 'D'):
                    _lm= nz.replace(c, 'L')
                else:
                    _lm= nz.replace(c, 'LC')
                zfile.extract(_lm)

    if len(_hm) == 0:
        #bad invoice file name  
        return ((1, 0), False)
    
    # import PMUs with tarifs
    if typ == 6:
        return imp_usl(_hm)

    #qonn = app.config.db()
    sn.qurs = g.qonn.cursor()
    #sn.qurs = qonn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    sn.qurs.execute(config.TRUNC_TBL_INV)
    #sn.qurs.execute(config.CREATE_TBL_INV)
    g.qonn.commit()
    
    # 2. process files
    # ---------------------------------------------
    for (f, r) in ( (_hm, sn.zap), (_lm, sn.pers)):
        zp_xml(f, r)
        g.qonn.commit()

    mek= set_mek(ar)
    
    sn.qurs.execute(config.COUNT_INV)
    rc= sn.qurs.fetchone()

    sn.qurs.close()

    os.remove(_hm)
    os.remove(_lm)
    #print (rc)
    return (( rc[0], mek), True) if bool(rc) and len(rc) > 0 else (( 2, 0), False)
