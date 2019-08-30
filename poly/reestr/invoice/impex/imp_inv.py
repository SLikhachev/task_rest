"""
"""
import sys, os, types
import xml.etree.cElementTree as ET
#from datetime import datetime
from pathlib import Path
from zipfile import ZipFile
from poly.reestr.invoice.impex import config
#import psycopg2
#import psycopg2.extras

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
    
    zapq= '''INSERT INTO invoice (
        "n_zap", "id_pac", "spolis", "npolis",
        "usl_ok", "vidpom", "for_pom", "date_z_1", "date_z_2", "rslt", "ishod",
        "profil", "nhistory", "ds1", "prvs",
        "idsp", "sumv", "sank_it"
    ) VALUES (
        %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s
    )''',
    
    pers= ( 'id_pac', 'fam', 'im', 'ot', 'w', 'dr'),
    
    persq= 'UPDATE invoice SET fam=%s, im=%s, ot=%s, w=%s, dr=%s WHERE id_pac=%s;',

    trunc_inv= 'TRUNCATE TABLE invoice;',
    trunc_meta= 'TRUNCATE TABLE invoice_meta;',
    count= 'SELECT count(n_zap) FROM invoice;',
    
    zp_tags = ('ZAP', 'PERS',),
    
    meta= {}
 )

def get_text(elem: ET.Element, tag: str) -> str:
    e= elem.find(tag)
    if hasattr(e, 'text'):
        return e.text
    return None

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
        sn.qurs.execute(sn.zapq, rec)
    else:
        # first el is id_pac
        rec.append( rec.pop(0) )        
        sn.qurs.execute(sn.persq, rec)

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

def get_meta(app: object, name: str, typ: int) -> bool:
    
    global sn
    hdr, tail= name.split('_')
    s= hdr.find('S') + 1
    if s <= 0:
        smo= ''
    else:
        smo= hdr[s+3:]
    lpu= tail[4:7]
    #app.logger.debug( lpu )
    if lpu not in app.config['MO_CODE']:
        return False
    sn.meta['lpu']= lpu
    sn.meta['smo']= smo
    sn.meta['yar']= tail[:2]
    sn.meta['mon']= tail[2:4]
    sn.meta['typ']= typ
    return True
    
def imp_inv(app: object, zipfile: str, typ: int) -> tuple:
    # app - flask app
    # name - file to process
    # typ - invoice type
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
            if nz.startswith('HM') or nz.startswith('CM'):
                
                #get_meta(current_app, nz, typ)
                if not get_meta(app, nz, typ):
                    return (0,)
                
                zfile.extract(nz)
                _hm= nz
                if nz[0] == 'H':
                    _lm= nz.replace('H', 'L')
                else:
                    _lm= nz.replace('CM', 'LCM')
                zfile.extract(_lm)

    if len(_hm) == 0:
        return (-1,)

    qonn = app.config.db()
    sn.qurs = qonn.cursor()
    #sn.qurs = qonn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    sn.qurs.execute(sn.trunc_inv)
    sn.qurs.execute(sn.trunc_meta)
    qonn.commit()
    
    # 2. process files
    # ---------------------------------------------
    for (f, r) in ( (_hm, sn.zap), (_lm, sn.pers)):
        zp_xml(f, r)
        qonn.commit()
    
    sn.qurs.execute(sn.count)
    rc= sn.qurs.fetchone()
    
    sn.qurs.execute(config.SET_META, (
        sn.meta['lpu'], sn.meta['smo'], sn.meta['yar'], sn.meta['mon'], sn.meta['typ'])
    )
    qonn.commit()
    
    sn.qurs.close()
    qonn.close()
    
    os.remove(_hm)
    os.remove(_lm)
    
    return ( rc[0], sn.meta['smo'], sn.meta['mon'],  sn.meta['yar'] ) 
