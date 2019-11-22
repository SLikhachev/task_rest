
# write sql data to xml files
# USAGE:
# sql_xml config, month, pack, nusl
# WHERE:
# config - name of python config file
# mohth - 2 digit month '01'- '12'
# pack - 2 digit pack number def ('01')
# nsul - string of distinct nusl number (talon number) def None

import os, sys, importlib, zipfile
from tempfile import TemporaryFile as tmpf
#from pathlib import Path
#import json
import xml.etree.cElementTree as ET
import psycopg2
import psycopg2.extras
from datetime import date, datetime
from poly.reestr.xml.pack.xml_class.pmHdrFile import PmData, PmHdr, PmSluch
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


def write_sluch(data, file, pm, usl, usp, stom=None):
#def write_sluch(data, pm, usl, stom=None):

    pm.set_usl('usl', data, usl, usp)
    if stom and len(stom) > 0:
        pm.set_usl('stom', stom)
    
    sluch= pm.get_sluch( data )
    
    ET.ElementTree( sluch ).write(file, encoding="unicode" )
    file.write('\n')

        
def write_zap(data, file, hm, usl, usp, stom=None):
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

    ET.ElementTree( hm.get_zap( data ) ).write(file, encoding="unicode" )
    file.write('\n')

    #if data.q_u == 3:
    #    hm.reset_ksg()


def write_pers(data, file, lm):
    pers= lm.get_pers( data )
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
    
def write_data(_app, mo, year, month, pack, sent, xmldir, stom=False, nusl=None ):

    """
    # mo: string(3) head MO code
    # year: int year 4 digit 
    # month: int month 2 digits
    #sent: bool if true ignore already sent records else not
    # xmldir: string working xml directory
    # qurs/1 : db cursor
    # stom bool for use stom pmu table in the prosess
    # nusl: string for AND condition of SQL SELECT statement or ''

    """
    
    qonn = _app.config.db()
    qurs = qonn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    qurs1 = qonn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    
    pmSluch = PmSluch(mo)
    hmZap = HmZap(mo)
    lmPers= LmPers(mo)
    rc = 0
    
    #print('-- WRITE HPL DATA --\n')
    ya= int(str(year)[2:])
    query= _sql.get_hpm_data % ya
    if sent:
        query= f'{query}{_sql.sent}'
    query=f'{query}{_sql.month}'
    qurs.execute(query, (month, ))


    #pmFile= open( f'{xmldir}pm.xml', 'r+')
    #hmFile= open( f'{xmldir}hm.xml', 'r+')
    #lmFile= open( f'{xmldir}lm.xml', 'r+')
    errFname= f'{xmldir}\\pak_error.txt'
    errorFile= open( errFname, 'w')
    
    pmFile= tmpf(mode="r+")
    hmFile = tmpf(mode="r+")
    lmFile = tmpf(mode="r+", encoding='1251')
    errors= 0
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
            _data = PmData(rdata)
            write_sluch(_data, pmFile, pmSluch, _usl, _usp, _stom)
            
            _data = HmData(rdata, _nmo)
            write_zap(_data, hmFile, hmZap, _usl, _usp)
            
            _data = LmData(rdata)
            write_pers(_data, lmFile, lmPers)
        except Exception as e:
            errorFile.write( f'{e}\n' )
            #qurs1.execute(_sql.set_error, (rdata.idcase, e))
            errors += 1
            continue
        
        # mark as sent
        qurs1.execute(_sql.set_as_sent, (ya, rdata.idcase))
        rc += 1

        #print(' rec %s ' % rc, end='\r')
    if errors > 0:
        errorFile.close()
        qurs.close()
        qurs1.close()
        qonn.commit()
        qonn.close()
        
        for f in (hmFile, pmFile, lmFile):
            f.close()
            
        return rc, len(lmPers.uniq), errFname, errors
        
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
    qonn.commit()
    qonn.close()
    
    return rc, len(lmPers.uniq), os.path.join(xmldir, zfile), 0


def make_xml(current_app, year, month, pack, sent):
     
    mo = current_app.config['MO_CODE'][0]
    xmldir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reestr', 'xml')
    #current_app.logger.debug(xmldir)
    
    return write_data(current_app, mo, year, month, pack, sent, xmldir, stom=False, nusl=None)


