import sys
from poly.reestr.invoice.tarif import config

class TarifSql:
    
    getData = 'SELECT %s FROM %s'
    getBase = getData % (config.BASE_TABLE[0], config.BASE_TABLE[1])
    getGonorar = getData % (config.GONORAR_TABLE[0], config.GONORAR_TABLE[1])
    getUrgent = getData % (config.URGENT_TABLE[0], config.URGENT_TABLE[1])
    getVzaimo = getData % (config.VZAIMO_TABLE[0], config.VZAIMO_TABLE[1])
    getVzaimoPmu = getData % (config.VZAIMO_PMU_TABLE[0], config.VZAIMO_PMU_TABLE[1])
    getStom = getData % (config.STOM_TABLE[0], config.STOM_TABLE[1])
    getStomPmu = getData % (config.STOM_PMU_TABLE[0], config.STOM_PMU_TABLE[1])
    getKsg = getData % (config.KSG_TABLE[0], config.KSG_TABLE[1])
    
    def __init__(self, db):
        self.qurs = db.cursor()
        self.base = self.get_data(TarifSql.getBase)
        self.gonorar = self.get_data(TarifSql.getGonorar)
        self.vzaimo = self.get_data(TarifSql.getVzaimo)
        self.vzaimo_pmu = self.get_data(TarifSql.getVzaimoPmu)
        self.neotl = self.get_data(TarifSql.getUrgent)
        self.stom_uet = self.get_data(TarifSql.getStom)
        self.stom_pmu = self.get_data(TarifSql.getStomPmu)
        self.ksg = self.get_data(TarifSql.getKsg)
        self.qurs.close()
        
    def get_data(self, data):
        self.qurs.execute(data)
        d = {}
        for el in self.qurs.fetchall():
            d[ el[0] ] = []
            for i in range(1, len(el)):
                d[ el[0] ].append( el[i] ) 
        return d
    
    def close(self):
        self.qurs.close()

    
class Tarif(TarifSql):

    _para = 'SELECT code_usl, kol_usl FROM para_clin WHERE tal_num=%s'

    def __init__(self, db, mo):
        TarifSql.__init__(self, db)
        self.qurs = db.cursor()
        self.rpq = Tarif._para
        self.row = None
        self.sluch = None
        self.none = (0.0, 0.0, 'None')
        self.mo = mo # list
        
    def set_data(self, row):
        self.row = row
        self.para = None
        #self.stom = None
        self.sluch = 0
        if (row.visit_pol + row.visit_home)  > 1:
            self.sluch = 1 
        return self
    
    def get_para(self):
        self.qurs.execute(self.rpq, ( self.row.n_zap, ) )
        self.para = self.qurs.fetchall()
        return self
    
    def get_stom(self):
        self.curs.execute(self.rsq, (self.row.n_zap, ))
        self.stom = self.curs.fetchall()
        return self
    
    def process(self):
        
        #stomatolog
        if self.row.profil in config.STOM:
            return self.set_stom()
        
        # urgent
        if self.row.for_pom == config.NEOTL:
            return self.set_urgent()
        
        # stacionar
        if self.row.usl_ok == config.DAY_STAC:
            return self.set_day_stac()
        
        # inokray
        if self.row.smo == 0:
             return self.none
             #return self.set_vzaimoras_gonor(self.vzaimo, 'inokray')
        
        # gonorar
        if int(self.row.profil) in self.gonorar.keys():
            return self.set_vzaimoras_gonor(self.gonorar, 'gonor')
        
        # vzaimoras
        if ((self.row.npr_mo is not None) and (self.row.npr_mo not in self.mo)) \
            or (int(self.row.doc_spec) in config.DETY_TRAVMA) \
            or (self.row.profil in config.GONOR_PROF):
            return self.set_vzaimoras_gonor(self.vzaimo, 'vzaimo')
        
        # profosmotr
        if self.row.purp in config.PROF:
             return self.set_prof()
        
        # attched
        return self.set_by_soul()
    
    def sum_para(self):
        self.get_para()
        tr, para = 0.0, 0.0
        for p in self.para:
            pt = self.vzaimo_pmu.get(p[0], None)
            if pt is None:
                continue
            tr = pt[0] # last non zero tarif
            para += pt[0] * int( p[1] )
        #if tr == 0.0: tr = self.base['BSL'][0]
        return tr, para
    
    def set_stom(self):
        code_usl = 0
        code_nom = 0
        self.get_stom().get_para()
        tarif = self.gonorar.get(self.row.profil, 0.0)
        uet = 0.0
        for s in self.stom:
            u = self.stom_uet.get(s[code_usl], None)
            if u is None:
                continue
            uet += u[0]
        for p in self.para:
            u = self.stom_pmu.get(p[code_nom], None)
            if u is None:
                continue
            uet += u[0] * p[1]
        #print(tarif, uet)    
        return ( tarif[0], round(tarif[0] * uet, 2), 'stom' )
        
    def set_urgent(self):
        tarif = self.neotl.get( int(self.row.doc_spec), self.neotl[0] )
        #tr, para = self.sum_para()
        sum = float( tarif[0] ) #+ para
        return (tarif[0], round( sum, 2), 'urgent')
        
    def set_day_stac(self):
        ksg = self.ksg.get( self.row.ksg, None)
        #print(self.row.code_mes, ksg)
        if ksg is None:
            return self.none
        kf = 1
        for k in ksg:
            kf *= k
        kt = 1.0
        if (self.row.visit_homstac + self.row.visit_daystac) <= 3:
            kt = 0.5
        tarif = float( self.base['KSG'][0] ) * kt
        return (tarif, round( tarif * kf, 2), 'stac' )

    def set_vzaimoras_gonor(self, starif, event):
        tarif = starif.get( self.row.profil , None)
        tr, para = self.sum_para()
        
        if tarif is not None:  
            tr = float( tarif[self.sluch] )
            # cost of para + tarif
            para += tr
  
        return (round(tr, 2), round(para, 2), event)
    
    def set_prof(self):
        tr = 0.0 #float(self.row.mr)
        return (tr, tr, 'prof')
    
    def set_by_soul(self, use_para=False, include_para=True):
        # set tarifs from vzaimo
        tarif = self.vzaimo.get(self.row.profil, None)
        #sum = 0.0
        tarif_para, para = self.sum_para()
        tarif_base = float( self.base['BSL'][0] )
        sum = tarif_base
        if tarif is None: # no such profil in vzaimo
            if use_para:
                tarif = tarif_para # last para tarif from para or tarif_base
            else:
                # no such spec in vzaimo use base
                tarif = tarif_base
            '''
            if self.row.profil in config.SESTRA:
                tarif , sum = tarif_base, tarif_base
            '''
            #sum = tarif_base
        else:
            tarif = tarif[self.sluch]
            # summ is tarif_base + para
            #sum = tarif_base
            
        # include paraclinic if need
        #sum = float(sum)
        if include_para:
             sum += para
        return ( round(tarif, 2), round(sum, 2), 'soul')
        
    def close(self):
        self.qurs.close()