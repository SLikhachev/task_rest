import re
from . import hosp_config as config
#import hosp_config as config # for test
from datetime import date

class HospEir:
    
    CLEAR_TABLE = 'TRUNCATE TABLE %s'
    
    def __init__(self, db, logger):
        self.table = 'hospital'
        # self func return native python objects
        self.logger = logger
        self.none = lambda _ : None
        self.fields = (
            ("nap_num",  self.to_int), 
            ("nap_date", self.to_date),
            ("for_pom", self.get_for_pom),
            ("usl_ok", self.get_usl_ok),
            ("to_mo", self.get_mo),
            ("date_hosp", self.to_date),
            ("p_ser", self.to_str),
            ("p_num", self.to_str),
            ("smo", self.get_smo),
            ("fam", self.to_str),
            ("im", self.to_str), 
            ("ot", self.to_str),
            ("date_birth", self.to_date),
            ("ds", self.get_ds),
            ("prof", self.none),
            ("host_stat", self.to_int),
            ("ann_stat", self.to_int),
            ("nap_hospl", self.to_int),
            ("date_hospl", self.to_date),
            ("mo_hospl", self.get_mo),
            ("act_date_hospl", self.to_date),
            ("for_pom_hospl", self.get_for_pom),
            ("specfic", self.get_doc)
        )
        
        self.cols = ', '.join( [ '"%s"' % c for c, _ in self.fields] )
        self.vals = ', '.join( [ '%s' for _, _ in self.fields] )
        self.qonn = db
        self.qurs = db.cursor()
    
    def clear_tbl(self):
        self.qurs.execute(HospEir.CLEAR_TABLE % self.table)
        self.qonn.commit()
        #print(' table truncated ')
        if self.logger:
            self.logger.info('table truncated')
        
    def to_str(self, val):
        if val == '':
            return None
        return val
    
    def to_int(self, val):
        if val == '':
            return None
        try:
            return int(val)
        except ValueError:
            return None
    
    def to_date(self, val):
        if val == '':
            return None
        try:
            d, m, y = val.split('.')
            return date(int(y), int(m), int(d))
        except Exception:
            return None
            
    def get_from_db(self, q):
        try:
            self.qurs.execute(q)
            v = self.qurs.fetchone()
            #print(v)
            if len(v) == 0:
                return None
            return v[0]
        except Exception:
            return None
    
    def get_for_pom(self, val):
        q = "select id from public.for_pom where name ilike '%s'" % val
        #print(q)
        return self.get_from_db(q)
    
    def get_usl_ok(self, val):
        q = "select id from public.usl_ok where name ilike '%s'" % val
        return self.get_from_db(q)
        
    def get_mo(self, val):
        q = "select scode from public.mo_local where similarity (name, '%s') > 0.9" % val
        #print(q)
        return self.get_from_db(q)
    
    def get_smo(self, val):
        return config.SMO.get(val, None)
    
    def get_ds(self, val):
        q = "select code from public.mkb10 where name ilike '%s'" % val 
        return self.get_from_db(q)
    
    def get_doc(self, val):
        if val == '' or len(val) < 4:
            return None
        d= re.search('(^\d+)([ ,./])*(\d+$)', val)
        if d is None:
            return None
        if d.group(2) is not None:
            spec, code = int(d.group(1)), int(d.group(3))
        else:    
            p= len(d.group(0)) # min 2
            spec, code = int(d.group(0)[:p-1]), int(d.group(0)[p-1:])
        q = 'select family from doctor where spec = %i and code = %i' % (spec, code) 
        if self.get_from_db(q) is not None:
            return '%i.%i' % (spec, code) 
        return None
        
    def getData(self, data):
        # data arr of strings filds
        '''
        for f, val in enumerate(data):
            print(val)
            vv = self.fields[f][1](val)
            print(vv)
        return []
        '''
        
        #return ', '.join( [ self.fields[ f[1](val) ]  for f, val in enumerate(data) ] )
        s = [ self.fields[f][1](val) for f, val in enumerate(data) ]
        if s[0] is None: # nap num must be int
            return None
        return s
        
    def close(self):
        self.qurs.close()
        
        
        
        
        