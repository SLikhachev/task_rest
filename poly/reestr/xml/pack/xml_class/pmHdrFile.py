
import xml.etree.cElementTree as ET
from datetime import date
#from collections import deque
#deque(map(writer.writerow, data), maxlen=0)
from poly.reestr.xml.pack.xml_class.mixTags import HdrMix, TagMix
from poly.reestr.xml.pack.xml_class.utils import DataObject


class PmData(DataObject):
    # here we set all params
    def __init__(self, ntuple):
        super().__init__(ntuple)
        # 1 - invoice
        # 2 - by soul 
        self.type_pay= 1 # yet
        
"""        
    @property
    def type_pay(self):
        return 1
"""

class PmUsl(DataObject):
    
    def __init__(self, mo, ntuple):
        super().__init__(ntuple)
        self.mo = mo
        self.executor= self.fmt_000(mo) + self.fmt_000(self.podr) + self.fmt_000(self.spec)
        self.ex_spec= self.fmt_000(self.npr_mo) + self.fmt_000(self.npr_spec)

# posechenue obraschenie 
class PmUsp(DataObject):
    """ USP
        tal.open_date as date_usl,
        prof.one_visit as code_usl1,
        prof.two_visit as code_usl2,
        1 as kol_usl, 
        prof.podr as podr, 
        tal.doc_spec as spec,
        tal.doc_code as doc,
    """
    def __init__(self, mo, ex_spec, ntuple):
        super().__init__(ntuple)
        self.mo = mo
        self.executor= self.fmt_000(mo) + self.fmt_000(self.podr) + self.fmt_000(self.spec)
        self.ex_spec= ex_spec
        

class PmHdr(HdrMix):
    
    def __init__(self, mo, year, month, pack, sd_z=None, summ=None):
        super().__init__(mo, year, month, pack)
        self.filename= self.p_file
        self.filename1= self.h_file
        #print(self.endTag)
        self.zglv_tags= (
            'data',
            'filename',
            'filename1',
        )
        self.zglv= ('ZGLV', self.zglv_tags)
        self.schet_tags= (
            'year',
            'month',
            'code_mo',
            'lpu'
        )
        self.schet= ('SCHET', self.schet_tags)

    
class PmSluch(TagMix):
    
    def __init__(self, mo):
        super().__init__(mo)
        self.usl = None
        self.stom = None
        self.sl_id = 1
        
        self.usl_tags = (
            'idserv',
            'executor', #self.executor
            'ex_spec', #self.ex_spec
            'rl' # ignore
        )
        self.stom_tags = (
            'idstom',
            'code_usl', #
            'zub',
            'kol_viz',
            'uet_fakt'
        )
        self.sluch_tags = (
            #'SL',
            'sl_id', #self..sl_id
            'idcase', #tal.tal_num
            'card', #tal.crd_num
            'from_firm', #tal.npr_mo
            'purp', #tal.purp
            'visit_pol', #tal.vsit_pol
            'visit_hom', #tal.visit_home
            'nsndhosp', #tal.nsndhosp
            'specfic', #tal.doc_spec
            'type_pay', #self.type_pay
            'd_type', #tal.d_type
            'naprlech', #tal.naprlech
            ('usl', self.usl_tags, 'list'),
            ('stom', self.stom_tags, 'list')
        )
        self.sluch = ( ('SL', self.sluch_tags) )

        self.ignore = (
            #'stom',
            'rl'
        )
        # dummy counted tags 
        self.cnt = (
            'idserv',
            'idstom',
        )
        self.required= (

        )
    
    def set_usl(self, tag, usl_list, usp):
        
        if not isinstance(usl_list, list):
            _u = [usl_list]
        else:
            _u = usl_list
        u_list = [ PmUsl(self.mo, u) for u in _u ]
        if len(u_list) == 0: # no PMU
            ex_spec= None
        else:
            ex_spec= u_list[-1].ex_spec
        
        # append posesh obrasch codes
        u_list.append( PmUsp(self.mo, ex_spec, usp) )
        
        setattr(self, tag, u_list)
        return self
    
    def get_sluch(self, data):
        #return self.wrap_tags( self.sluch[0], self.sluch[1:], data)
         return self.make_el( self.sluch, data)
    
