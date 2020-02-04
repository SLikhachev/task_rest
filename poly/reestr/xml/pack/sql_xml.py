
# write sql data to xml files
# USAGE:
# sql_xml config, month, pack, nusl
# WHERE:
# config - name of python config file
# mohth - 2 digit month '01'- '12'
# pack - 2 digit pack number def ('01')
# nsul - string of distinct nusl number (talon number) def None

import os, sys, importlib, zipfile, time
from tempfile import TemporaryFile as tmpf
#from pathlib import Path
#import json
import xml.etree.cElementTree as ET
import psycopg2
import psycopg2.extras
from flask import g
from datetime import date, datetime
from poly.reestr.xml.pack.xml_class.pmHdrFile import PmData, PmHdr, PmSluch, dcons
from poly.reestr.xml.pack.xml_class.hmHdrFile import HmData, HmHdr, HmZap
from poly.reestr.xml.pack.xml_class.lmHdrFile import LmData, LmHdr, LmPers
from poly.reestr.xml.pack.xml_class.mixTags import HdrMix
from poly.reestr.xml.pack import config_sql as _sql


def write_hdr(hdr, mo, year, month, pack, xmldir, fm_temp, sd_z=None, summ=None):
    _hdr = hdr(mo, year, month, pack, sd_z, summ)
    _name = '%s\\%s%s' % (xmldir, _hdr.filename, '.xml')
    _file = open(_name, 'w', encoding='1251')
    _file.write( '%s\n' % _hdr.startTag )
        
    ET.ElementTree(_hdr.get_zag( _hdr )).write(_file, encoding="unicode" )
    _file.write('\n')
    schet= _hdr.get_schet(_hdr) # LM class returns None

    if schet is not None:
        ET.ElementTree( schet ).write(_file, encoding="unicode" )
        _file.write('\n')

    for line in fm_temp:
        _file.write(line)

    _file.write( _hdr.endTag )
        # hmFile.write('%s\n' % hmHdr.endTag)

    # (file object, hdr instance)
    _file.close()
    #print (_name)
    return f'{_hdr.filename}.xml'


def write_sluch(check, data, file, pm, usl, usp, stom=None):
#def write_sluch(data, pm, usl, stom=None):
    
    assert (data.specfic in dcons) and len(usl) > 0, f'{data.idcase}-Для спец. {data.specfic} нет ПМУ'
    
    pm.set_usl('usl', data, usl, usp)
    if stom and len(stom) > 0:
        pm.set_usl('stom', stom)
    
    sluch= pm.get_sluch( data )
    if check:
        return
    ET.ElementTree( sluch ).write(file, encoding="unicode" )
    file.write('\n')

        
def write_zap(check, data, file, hm, usl, usp, stom=None):
    hm.set_usl('usl', usl, usp, data)
    """
    if data.q_u == 3:
        hm.set_ksg(data.n_ksg)
        data.p_per = 1
    else:
        data.profil_k = None
        data.npr_data = None
        data.p_per = None
        hm.reset_ksg()
    """
    zap= hm.get_zap( data )
    if check:
        return 
    ET.ElementTree( zap ).write(file, encoding="unicode" )
    file.write('\n')

    #if data.q_u == 3:
    #    hm.reset_ksg()


def write_pers(check, data, file, lm):
    pers= lm.get_pers( data )
    if check:
        return
    if pers:
        ET.ElementTree( pers ).write(file, encoding="unicode" )
        file.write('\n')

def get_npr_mo(qurs, rdata):
    if bool(rdata.cons_mo):
        _nmo= rdata.cons_mo
    elif bool(rdata.hosp_mo):
        _nmo= rdata.hosp_mo
    else:
        return None
    qurs.execute(_sql.get_npr_mo, (_nmo,))
    m= qurs.fetchone()
    if m:
        return m.code
    return None
    
def write_data(
    _app: object, mo: str, year: int, month: int, pack: str,
    check: bool, sent: bool, fresh: bool,
    xmldir: str, stom=False, nusl='') -> tuple:

    """
    # _app: obj, current app FLASK object
    # mo: string(3) head MO code
    # year: int year 4 digit 
    # month: int month 2 digits
    # pack: string(2), pack number
    # check: if TRUE -> check tables recs only, don't make xml pack
    #   else make zip xml pack and fill error_pack table, dont make error_pack
    # sent: bool if true set records field talon_type = 2 else ignore 
    # fresh: bool if true ignore already sent and accepted records else not make full pack
    # xmldir: string working xml directory
    # stom bool for use stom pmu table in the prosess
    # nusl: string for AND condition of SQL SELECT statement or ''

    """
    
    #qonn = _app.config.db()
    qurs = g.qonn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    qurs1 = g.qonn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    
    pmSluch = PmSluch(mo)
    hmZap = HmZap(mo)
    lmPers= LmPers(mo)
    
    #pmFile= open( f'{xmldir}pm.xml', 'r+')
    #hmFile= open( f'{xmldir}hm.xml', 'r+')
    #lmFile= open( f'{xmldir}lm.xml', 'r+')
    errFname= f'{xmldir}\\error_pack_{time.time()}.csv'
    errorFile= open( errFname, 'w') if check else None
    qurs1.execute(_sql.truncate_errors)
    g.qonn.commit()
    
    # make pack anyway if not check, just ignore all errors 
    pmFile= tmpf(mode="r+") if not check else None
    hmFile = tmpf(mode="r+") if not check else None
    lmFile = tmpf(mode="r+", encoding='1251') if not check else None

    ya = int(str(year)[2:])
    query = _sql.get_hpm_data % ya
    if fresh:
       # talon_type == 1 only will be included in pack 
        query = f'{query}{_sql.fresh}'
    else:
        #type > 0
        query = f'{query}{_sql.all_tal}'

    query = f'{query}{_sql.month}'
    qurs.execute(query, (month,))
    rc = errors = 0
    for rdata in qurs:
        _nmo= get_npr_mo(qurs1, rdata)
        qurs1.execute(_sql.get_usl, ( ya, ya, rdata.idcase, ) )
        _usl = qurs1.fetchall()
        # specaial usl for posesh obrasch
        qurs1.execute(_sql.get_spec_usl, (ya, rdata.idcase, ) )
        _usp = qurs1.fetchone()
        _stom= list()
        if stom:
            qurs1.execute(_sql.get_stom, ( rdata.idcase, ) )
            _stom = qurs1.fetchall()
        
        try:
            _data = PmData(rdata, mo)
            write_sluch(check, _data, pmFile, pmSluch, _usl, _usp, _stom)
            
            _data = HmData(rdata, _nmo)
            write_zap(check, _data, hmFile, hmZap, _usl, _usp)
            
            _data = LmData(rdata)
            write_pers(check, _data, lmFile, lmPers)
        
        except Exception as e:
            if errorFile:
                errorFile.write( f'{rdata.card}-{e}\n' )
            
            qurs1.execute(_sql.set_error, (rdata.idcase, rdata.card, str(e).split('-')[1] ) )
            errors += 1
            continue
        
        # mark as sent
        if not check and sent:
            qurs1.execute(_sql.mark_as_sent, (ya, rdata.idcase))
        rc += 1

    # check data routine
    if check: # errors > 0 and check: # return error_pack file
        errorFile.close()
        qurs.close()
        qurs1.close()
        g.qonn.commit()
        
        if not bool(errors):
            os.remove(errFname)
            errFname= ''
            
        return rc, len(lmPers.uniq), errFname, errors

    # no right records found
    if not bool(rc):
        for f in (hmFile, pmFile, lmFile):
            if f: f.close()
        qurs.close()
        qurs1.close()
        g.qonn.commit()
        return rc, rc, '', errors
        
    # make zip file anyway and return it
    to_zip=[]
    for f, h in ((hmFile, HmHdr), (pmFile, PmHdr), (lmFile, LmHdr)):
        f.seek(0)
        to_zip.append( write_hdr(h, mo, year, month, pack, xmldir, f, sd_z=rc, summ='0.00') )
        f.close()

    _p = HdrMix(mo, year, month, pack)
    os.chdir(xmldir)
    zfile=f'{_p.pack_name}'
    with zipfile.ZipFile(zfile, 'w', compression=zipfile.ZIP_DEFLATED) as zipH:
        for f in to_zip:
            zipH.write(f)
    
    #_app.logger.debug(lmPers.dubl)    
    
    qurs.close()
    qurs1.close()
    g.qonn.commit()
    #qonn.close()
    
    return rc, len(lmPers.uniq), os.path.join(xmldir, zfile), errors


def make_xml(current_app, year, month, pack, check, sent, fresh):
     
    mo = current_app.config['MO_CODE'][0]
    xmldir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reestr', 'xml')
    #current_app.logger.debug(xmldir)
    
    return write_data(
        current_app, mo, year, month, pack,
        check, sent, fresh,
        xmldir, stom=False, nusl=None)


