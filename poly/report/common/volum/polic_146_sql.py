# --*-- coding='UTF-8' --*--

# filll p146_report table with current month values

#import sys
#from datetime import date
import psycopg2
import psycopg2.extras
#import volumes_146_order.config_146 as config

class Report(object):

    GET_TABLE = '''SELECT table_name FROM INFORMATION_SCHEMA.TABLES
        WHERE table_type='BASE TABLE' AND table_name = '%s';'''

    INS_AMBUL = '''INSERT INTO p146_report
            (this_year, this_month, insurer, pol_ambul_visits, pol_ambul_persons)   
            VALUES (%s, %s, %s, %s, %s)'''
    UPD_AMBUL = '''UPDATE p146_report SET
            pol_ambul_visits=%s, pol_ambul_persons=%s   
            WHERE this_year=%s AND this_month=%s AND insurer=%s;'''
    
    INS_PROF = '''INSERT INTO p146_report
            (this_year, this_month, insurer, pol_prof_visits, pol_prof_persons)   
            VALUES (%s, %s, %s, %s, %s)'''
    UPD_PROF = '''UPDATE p146_report SET
            pol_prof_visits=%s, pol_prof_persons=%s   
            WHERE this_year=%s AND this_month=%s AND insurer=%s;'''
    
    UPD_STAC = '''UPDATE p146_report SET pol_stac_visits=%s, pol_stac_persons=%s 
            WHERE this_year=%s AND this_month=%s AND insurer=%s;'''
    UPD_STOM = '''UPDATE p146_report SET pol_stom_uet=%s, pol_stom_persons=%s 
            WHERE this_year=%s AND this_month=%s AND insurer=%s;'''
    
    INS_TOTAL = '''INSERT INTO p146_report 
            (this_year, this_month, insurer, 
            pol_ambul_visits, pol_prof_visits, pol_stac_visits, pol_stom_uet, 
            pol_ambul_persons, pol_prof_persons, pol_stac_persons, pol_stom_persons) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    UPD_TOTAL = '''UPDATE p146_report SET
            pol_ambul_visits=%s, pol_prof_visits=%s, pol_stac_visits=%s, pol_stom_uet=%s, 
            pol_ambul_persons=%s, pol_prof_persons=%s, pol_stac_persons=%s, pol_stom_persons=%s 
            WHERE this_year=%s AND this_month=%s AND insurer=%s;'''

    INS_TRAVMA = '''INSERT INTO p146_report
            (this_year, this_month, insurer, travma_ambul_visits, travma_ambul_persons) 
            VALUES (%s, %s, %s, %s, %s)'''
    UPD_TRAVMA = '''UPDATE p146_report SET
            travma_ambul_visits=%s , travma_ambul_persons=%s 
            WHERE this_year=%s AND this_month=%s AND insurer=%s;'''

    REPORT_INSURERS = 'SELECT insurer FROM p146_report WHERE this_year=%s AND this_month=%s;'

    RR_INSURERS = 'SELECT DISTINCT c_insur FROM %s'

    STOM_PROF = '(85, 86, 87, 88, 89, 90)'

    def __init__(self, rr_table):

        self.get_table = Report.GET_TABLE
       
        self.ins_ambul = Report.INS_AMBUL
        self.upd_ambul = Report.UPD_AMBUL

        self.upd_prof = Report.UPD_PROF
        self.ins_prof = Report.INS_PROF

        self.ins_travm = Report.INS_TRAVMA
        self.upd_travm = Report.UPD_TRAVMA

        self.upd_stac = Report.UPD_STAC
        self.upd_stom = Report.UPD_STOM

        self.ins_total = Report.INS_TOTAL
        self.upd_total = Report.UPD_TOTAL

        self.stom_prof = Report.STOM_PROF

        self.rr_insurers = Report.RR_INSURERS % rr_table

        # ambulance
        _pers = 'SELECT COUNT (*) FROM ( SELECT DISTINCT card FROM %s ' % rr_table
        _oms = ' WHERE ist_fin=1 '
        _no_stom = ' AND profil NOT IN %s ' % self.stom_prof
        _stom = ' AND profil IN %s ' % self.stom_prof
        _vpol = ' AND q_u = 2 '
        _ambul = ' AND purp <> 21 '
        _prof = ' AND purp = 21 '
        _vstac = ' AND q_u = 3 '
        _ins = ' AND c_insur = %s '
        #_ins_not = ' AND c_insur IS NOT NULL '

        _viz_pol = 'SELECT SUM(visit_pol) AS pol, SUM(visit_hom) AS hom FROM %s ' % rr_table
        _viz_stac = 'SELECT SUM(visit_ds) AS ds, SUM(visit_hs) AS hs FROM %s ' % rr_table
        _viz_travm = 'SELECT SUM(visit_pol) AS vpol FROM %s ' % rr_table

        # persons and vizit to polic with def insurer
        self.pers_vpol = _pers + _oms + _no_stom + _vpol + _ambul + _ins +') AS pambul'
        self.viz_vpol = _viz_pol + _oms + _no_stom + _vpol +_ambul + _ins

        # persons and vizit to profosmotr with def insurer
        self.pers_prof = _pers + _oms + _no_stom + _vpol + _prof + _ins +') AS pambul'
        self.viz_prof = _viz_pol + _oms + _no_stom + _vpol + _prof + _ins
 
        # persons and vizit to travma with def insurer
        self.pers_travm = _pers + _oms + _ins + ') AS ptravm'
        self.viz_travm = _viz_travm + _oms + _ins

        # persons and vizit to home and/or day stacionar with def insurer
        self.pers_stac = _pers + _oms + _vstac + _ins + ') AS pstac'
        self.viz_stac = _viz_stac + _oms + _vstac + _ins

        # persons stomatology with def insurer
        self.pers_stom = _pers + _oms + _stom + _ins + ') AS pstom'

        self.report_insurers = Report.REPORT_INSURERS

    
class FillReportTable(Report):

    def __init__(self, app, db, mo, month, year, stom=False, stac=False, write=False):
        
        self.app = app #obj current flask app
        self.db = db #obj current db connection

        self.mo = mo # string MO code
        self.month = month # int this month
        self.year = year # int this year

        self.stom = stom # bool flag to calculate stomatology
        self.stac = stac  # bool flag to calculate stacionar
        self.write = write #bool flag to write results to db table

        #self.stomStart = 500000  # stom talon start number
        #self.errorLast = 1000000  # records from last month (last month errors)

        self.total = '999' # virtual insurer for tatal numbers
        self.table = '%s_%s_%s_%s' # rr(s, p)_mo_month(2)_year(2)
        self.qurs = db.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        self._qurs = db.cursor()

        self.rr_table = self.r_table_name('rr')
        self.rp_table = self.r_table_name('rp')
        self.rs_table = self.r_table_name('rs')

        Report.__init__(self, self.rr_table)
        
        #self.report_insur_list = self.get_insur_list(self.report_insurers, int(year), month)
        #self.rr_insur_list = self.get_insur_list(self.rr_insurers)
        
    def test(self):
        self.app.logger.error(' rr_table %s' % self.rr_table)
        self.app.logger.debug(' init report insur list %s' % self.report_insur_list)
        self.app.logger.debug(' init rr insur list %s' % self.rr_insur_list)


    def r_table_name(self, name):
            if self.month < 10:
                month = '0%s' % self.month
            else:
                month = '%s' % self.month
            y = ('%s' % self.year)[2:]
            return self.table % (name, self.mo, month, y)

    def check_table(self, name):
        #self.app.logger.debug(self.get_table % name)
        self._qurs.execute(self.get_table % name)
        if self._qurs.fetchone():
            return True
        return False
             
    def table_test(self):
        if self.stom and self.check_table(self.rs_table) and self.check_table(self.rp_table):
            self.stom = True
        else:
            self.stom = False
        #self.app.logger.debug(' stom is %s' % self.stom)
        if self.check_table(self.rr_table):
            self.report_insur_list = self.get_insur_list(self.report_insurers, int(self.year), self.month)
            self.rr_insur_list = self.get_insur_list(self.rr_insurers)
            return True
        return False
    
    def get_insur_list(self, query, year=None, month=None):
        if year and month:
            self._qurs.execute(query, (year, month))
        else:
            self._qurs.execute(query)
        #self.app.logger.debug(' insur query %s' % query)
        return [i[0] for i in self._qurs.fetchall()]

    def stom_uet(self, insurer=None):

        uetq = 'SELECT SUM(uet_fakt) FROM %s '
        where = ' WHERE nusl = %s'
        uet_rp = (uetq % self.rp_table) + where
        uet_rs = (uetq % self.rs_table) + where

        _pers = '''SELECT nusl FROM %s 
            WHERE ist_fin=1 AND profil IN %s ''' % (self.rr_table, self.stom_prof)

        if insurer is not None:
            pers = _pers + 'AND c_insur = %s'
            self.qurs.execute(pers, (insurer,))
        else:
            pers = _pers + 'AND c_insur IS NOT NULL'
            self.qurs.execute(pers)
        rr = self.qurs.fetchall()

        uet = 0.0
        for r in rr:
            nusl = r[0]
            self.qurs.execute(uet_rp, (nusl,))
            try:
                urp = float( self.qurs.fetchone()[0] )
            except Exception as e:
                urp = 0.0
            self.qurs.execute(uet_rs, (nusl,))
            try:
                urs = float( self.qurs.fetchone()[0] )
            except Exception as e:
                urp = 0.0
            if urp:
                uet += urp
            if urs:
                uet += urs
        #self.app.logger.debug(' stom: insur=%s uet=%s' % ( insurer, uet) )
        #qurs.close()
        return uet

    def set_ambul_prof(self, insurer, prof=False):
        # prof 
        if prof:
            q_pers= self.pers_prof
            q_viz= self.viz_prof
            q_upd=self.upd_prof
            q_ins=self.ins_prof
        # ambulance
        else:
            q_pers= self.pers_vpol
            q_viz= self.viz_vpol
            q_upd=self.upd_ambul
            q_ins=self.ins_ambul
            
        self._qurs.execute(q_pers, (insurer,))
        pers = self._qurs.fetchone()[0]
        self.qurs.execute(q_viz, (insurer,))
        v = self.qurs.fetchone()

        pol = v.pol or 0
        hom = v.hom or 0
        viz = pol + hom
        #-- test --
        #self.app.logger.debug(' from set ambul -- %s -- pers_vpol %s -- visits %s --' % (insurer, pers, viz))
        if not self.write:
            return viz, pers # visits persons for insurer

        if insurer in self.report_insur_list:
            # first record either inserted or updated (if exists), other update only
            try:
                self._qurs.execute(q_upd, (viz, pers, self.year, self.month, insurer))
                self.db.commit()
                # pass
            except Exception as e:
                self.app.logger.error('set ambul/prof db error %s' % e)
                self.db.rollback()
                #sys.exit()
        else:
            try:
                self._qurs.execute(q_ins, (self.year, self.month, insurer, viz, pers))
                self.db.commit()
            except Exception as e:
                self.app.logger.error('set ambul/prof db error %s' % e)
                self.db.rollback()
                #sys.exit()

        return viz, pers # visits persons for insurer

    def set_travm(self, insurer):
        # ambulance travma
        self._qurs.execute(self.pers_travm, (insurer,))
        pers = self._qurs.fetchone()[0]
        self.qurs.execute(self.viz_travm, (insurer,))
        v = self.qurs.fetchone()

        viz = v.vpol or 0
        #-- test --
        if not self.write:
            return viz, pers # visits persons for insurer
        #-- test -- 
        if insurer in self.report_insur_list:
            try:
                self._qurs.execute(self.upd_travm, (viz, pers, self.year, self.month, insurer))
                self.db.commit()
                # pass
            except Exception as e:
                self.app.logger.error('set travma db error %s' % e)
                self.db.rollback()
                #sys.exit()
        else:
            try:
                self._qurs.execute(self.ins_travm, (self.year, self.month, insurer, viz, pers))
                self.db.commit()
            except Exception as e:
                self.app.logger.error('set travma db error %s' % e)
                self.db.rollback()
                #sys.exit()
        
        return viz, pers # visits persons for insurer

    def set_stac(self, insurer):
        # day stacionar
        self._qurs.execute(self.pers_stac, (insurer,))
        pers = self._qurs.fetchone()[0]
        self.qurs.execute(self.viz_stac, (insurer,))
        v = self.qurs.fetchone()

        ds = v.ds or 0
        hs = v.hs or 0
        days = ds + hs
        if not self.write:
            return days, pers # visits persons for insurer
        try:
            self._qurs.execute(self.upd_stac, (days, pers, self.year, self.month, insurer))
            self.db.commit()
        except Exception as e:
            self.app.logger.error('set sctac db error %s' % e)
            self.db.rollback()
            #sys.exit()

        return days, pers

    def set_stom(self, insurer):
        # stomatolog
        #print(self.pers_stom)
        self._qurs.execute(self.pers_stom, (insurer,))
        pers = self._qurs.fetchone()[0]
        #total_pers_stom += pers
        uet = self.stom_uet(insurer)
        #total_uet += uet
        if not self.write:
            return uet, pers
        try:
            self._qurs.execute(self.upd_stom, (uet, pers, self.year, self.month, insurer))
            self.db.commit()
        except Exception as e:
            self.app.logger.error('set stom db error %s' % e)
            self.db.rollback()
            #sys.exit()

        return uet, pers

    def set_total_ambul(self):
        total_pers_vpol = 0
        total_vpol = 0

        total_pers_prof = 0    
        total_prof = 0

        total_pers_stac = 0
        total_stac = 0

        total_pers_stom = 0
        total_uet = 0.0
        
        for ico in self.rr_insur_list:
            insurer = ico
            viz, pers = self.set_ambul_prof(insurer)
            total_pers_vpol += pers
            total_vpol += viz
            
            viz, pers = self.set_ambul_prof(insurer, prof=True)
            total_pers_prof += pers
            total_prof += viz
            
            if self.stac:
                days, pers = self.set_stac(insurer)
                total_pers_stac += pers
                total_stac += days

            if self.stom:
                uet, pers = self.set_stom(insurer)
                total_pers_stom += pers
                total_uet += uet

        # -- test -- 

        #self.app.logger.debug(' TOTAL ---')
        #self.app.logger.debug(' -- pers vpols %s -- visits %s --' % (total_pers_vpol, total_vpol))
        #self.app.logger.debug(' -- pers stac %s -- days %s --' % (total_pers_stac, total_stac))
        #self.app.logger.debug(' -- pers stom %s -- uet %0.2f --' % (total_pers_stom, total_uet))
        #return " Done ambul test "

        # -- test --
        if not self.write:
            return "Рассчитана поликлиника "
        if self.total in self.report_insur_list:
            #UPD_TOTAL = '''UPDATE p146_report SET
            #pol_ambul_visits=%s, pol_prof_visits=%s, pol_stac_visits=%s, pol_stom_uet=%s, 
            #pol_ambul_persons=%s, pol_prof_persons=%s, pol_stac_persons=%s, pol_stom_persons=%s 
            #WHERE this_year=%s AND this_month=%s AND insurer=%s;'''
            try:
                self._qurs.execute(self.upd_total, (
                    total_vpol, total_prof, total_stac, total_uet,
                    total_pers_vpol, total_pers_prof, total_pers_stac, total_pers_stom,
                    self.year, self.month, self.total))
                self.db.commit()
                # pass
            except Exception as e:
                self.app.logger.error('set ambul total db error %s' % e)
                self.db.rollback()
                #sys.exit()
        else:
            try:
                 self._qurs.execute(self.ins_total,
                    (self.year, self.month, self.total,
                     total_vpol, total_prof, total_stac, total_uet,
                     total_pers_vpol, total_pers_prof, total_pers_stac, total_pers_stom)
                  )
                 self.db.commit()
            except Exception as e:
                self.app.logger.error('set ambul total db error %s' % e)
                self.db.rollback()
                #sys.exit()
        return "Рассчитана поликлиника "

    def set_total_travm(self):
        total_pers_travm = 0
        total_travm = 0

        for ico in self.rr_insur_list:
            insurer = ico
            viz, pers = self.set_travm(insurer)
            total_pers_travm += pers
            total_travm += viz

        #self.app.logger.debug(' TOTAL TRAVM---')
        #self.app.logger.debug(' -- pers travm %s -- visits travm %s --' % (total_pers_travm, total_travm))
        #return " Done travm test "

        if not self.write:
            return " Рассчитана травма "
        if self.total in self.report_insur_list:
            try:
                self._qurs.execute(self.upd_travm, (total_travm, total_pers_travm,
                        self.year, self.month, self.total))
                self.db.commit()
                # pass
            except Exception as e:
                self.app.logger.error('set travma total db error %s' % e)
                self.db.rollback()
                #sys.exit()
        else:
            try:
                 self._qurs.execute(self.ins_travm,
                    (self.year, self.month, self.total,
                     total_travm, total_pers_travm)
                  )
                 self.db.commit()
            except Exception as e:
                self.app.logger.error('set travm total db error %s' % e)
                self.db.rollback()
                #sys.exit()
        return " Рассчитана травма "

    def __del__(self):
        self.qurs.close()
        self._qurs.close()
