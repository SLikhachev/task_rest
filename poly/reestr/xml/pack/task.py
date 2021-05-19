
from flask import request, current_app, g
from poly.reestr.task import RestTask
from poly.utils.fields import month_field
from poly.reestr.xml.pack.sql_xml import make_xml


class MakeXml(RestTask):

    def __init__(self):
        super().__init__()
        self.task= 'make_xml'

    def post(self):

        ts = self.open_task()
        if len(ts) > 0:
            return self.busy(ts)
        #ints
        self.year, self.month = month_field( request.form.get('month', '') )

        # pack number
        self.pack_num = request.form.get('pack', None)
        if not self.pack_num:
            self.pack_num = '01'
        
        ### if CHECK is  'check' then checlk only if 'ignore' then make reestr ignore errors
        # if chek is True to check only, else make reestr ignore errors
        check= False
        if bool(request.form.get('test', None)):
            check= True

        # if SENT is flase dont setup talon_type=2 as sent talon
        sent= fresh= False
        if bool(request.form.get('sent', None)):
            sent= True
        # if FRESH is false ignore already sent and accepted talons and produce full pack
        if bool(request.form.get('fresh', None)):
            fresh= True
        #current_app.logger.debug(year, month, pack, sent)
        try:
            if current_app.config.get('BARSXML', False):
                from poly.reestr.xml.pack import barsxml_config as bcfg
                from barsxml.xmlprod.barsxml import BarsXml  
                setattr(bcfg, 'YEAR', str(self.year))
                setattr(bcfg, 'db', g.qonn)
                #print(bcfg.db.dsn)
                xml = BarsXml(bcfg, 'xml', str(self.month), self.pack_num)
                ph, lm, file, errors =  xml.make_xml(sent, fresh, check)
            else:
                ph, lm, file, errors = make_xml(
                current_app, self.year, self.month, self.pack_num, check, sent, fresh)
            # if check is check, file is csv errors file
            # if check is None, ignore, file is pack.zip
        except Exception as e:
            self.abort_task()
            raise e
            #ex= printException()
            current_app.logger.debug( e )
            return self.close_task ('', f'Исключение: {e}', False)
        
        t= f'{self.perf()}'
        z= f'H записей: {ph}, L записей: {lm} '
        if errors > 0:
            msg = f'{z}, НАЙДЕНО ОШИБОК: {errors}. {t}'
            done = False
            # file -> zip if check is False else error_pack.csv
        else:
            if check: # == 'check':
                file= ''
            # file is NONE if no errors found and no request for pack to make 
            
            msg = f'{z}. {t}'
            done= True
            
        return self.close_task (file, msg, done)
