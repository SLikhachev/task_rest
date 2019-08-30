
#import xml.etree.cElementTree as ET
#from datetime import date
#from collections import deque
#deque(map(writer.writerow, data), maxlen=0)

#from tarif.tarif_class import TarifSql
#from tarif.config_tarif import TARIF_DB

from poly.reestr.xml.pack.xml_class.mixTags import HdrMix, TagMix
from poly.reestr.xml.pack.xml_class.utils import DataObject


class HmData(DataObject):
    
    def __init__(self, ntuple):
        super().__init__(ntuple)
        self.smo= f'250{self.smo}'
        self.npr_mo= f'250{self.npr_mo}'
        self.iddokt= self.iddokt.replace(" ", "-")

        self.calc = (
            self._os_sluch,
            self._idsp,
            self._pcel,
            self._vidpom,
            #self._sumv,
        )

        for func in self.calc:
            func()

    def _os_sluch(self):
        if self.ot is None:
            self.os_sluch = 2

    def _idsp(self):
        if self.usl_ok == 3:
            if (self.visit_pol + self.visit_hom) == 1:
                self.idsp = 29
            else:
                self.idsp = 30
        else:
            self.idsp = 33

    def _pcel(self):
        def pcel(for_pom, purp):
            if for_pom == 2:
                return '1.1'  # Посещениe в неотложной форме
            if purp == 7:  # Патронаж
                return '2.5'
            if purp in (1, 2, 6, 9):  # Aктивное посещение
                return '1.2'
            if purp in (10,):  # Диспансерное наблюдение
                return '1.3'
            if purp in (4, 5, 14, 20, 21):  # Медицинский осмотр
                return '2.1'
            return '2.6'  # Посещение по другим обстоятельствам

        self.p_cel = None
        if self.usl_ok != 3:
            return
        self.p_cel = pcel(self.for_pom, self.purp)

    def _vidpom(self):
        if self.profil in (78, 82):
            self.vidpom = 11
        elif self.prvs in (76) and self.profil in (97, 160):
            self.vidpom = 12
        else:
            self.vidpom = 13

    def _sumv(self):
        self.sumv= 0.0


class HmUsl(DataObject):
    
    def __init__(self, mo, ntuple, data):
        super().__init__(ntuple)
        self.lpu= f'250{mo}'
        self.profil= data.profil
        self.det= 0
        self.date_in= self.date_usl
        self.date_out= self.date_usl
        self.ds= data.ds1
        self.prvs= data.prvs
        self.code_md= data.iddokt
        if getattr(self, 'sumv_usl', None) is None:
            self.sumv_usl= 0



class HmUsp(HmUsl):
    """ USP
        tal.open_date as date_usl,
        prof.one_visit as code_usl1,
        prof.two_visit as code_usl2,
        1 as kol_usl, 
        prof.podr as podr, 
        tal.doc_spec as spec,
        tal.doc_code as doc,
    """
    def __init__(self, mo, ntuple, data):
        super().__init__(mo, ntuple, data)
        if data.idsp == 29:
            self.code_usl= self.code_usl1
        else:
            self.code_usl= self.code_usl2


class HmHdr(HdrMix):
    
    def __init__(self, mo, year, month, pack, sd_z, sumv):
        super().__init__(mo, year, month, pack)
        self.sd_z = '%s' % sd_z
        self.code = '%s%s%s' % (mo, year, month)
        self.nschet = self.code + '01'
        self.dschet = self.data
        self.summav = sumv
        self.filename= self.h_file

        self.zglv_tags= (
            'version',
            'data',
            'filename',
            'sd_z',
        )
        self.zglv = ('ZGLV', self.zglv_tags)
        self.schet_tags= (
            'code',
            'code_mo',
            'year',
            'month',
            'nschet',
            'dschet',
            'summav',
        )
        self.schet = ('SCHET', self.schet_tags)

        self.required= (
            'version',
            'data',
            'filename',
            'sd_z',
            'code',
            'code_mo',
            'year',
            'month',
            'nschet',
            'dschet',
            'summav',
        )

        
class HmZap(TagMix):
    
    def __init__(self, mo):
        super().__init__(mo)
        self.usl = None
        self.stom = None
        self.ksg_kpg = None
        self.sl_id = 1
        self.pr_nov = 0
        self.vers_spec = 'V021'
        self.det = 0
        self.novor= 0
        self.tariff= None

        self.ksg_class_inst = type('Ksg', (object, ), {})()
        setattr(self.ksg_class_inst, 'ver_ksg', '2018')
        setattr(self.ksg_class_inst, 'ksg_pg', 0)
        setattr(self.ksg_class_inst, 'sl_k', 0)
        self.sl_koef = None
        
        #self.tdb = psycopg2.connect(TARIF_DB)
        #self.tarifs = TarifSql(self.tdb)
        
        self.pacient_tags = (
            'id_pac', #tal.crd_num
            'vpolis', #crd.polis_type
            'spolis', #crd.polis_ser
            'npolis', #crd.polis_num
            'st_okato', #crd.st_okato
            'smo', # crd.smo
            'smo_ogrn', #crd.smo_ogrn
            'smo_ok', #crd.smo_okato
            'smo_nam', #crd.smo_name
            'inv', # ignore
            'mse', #ignore
            'novor',
            'vnov_d', #igmore
        )
        
        self.sl_koef_tags = (
            'idsl',
            'z_sl',
        )
        
        self.ksg_tags = (
            'n_ksg',
            'ver_ksg', 
            'ksg_pg',
            'n_kpg', 
            'koef_z',
            'koef_up',
            'bztsz',
            'koef_d',
            'koef_u',
            'dkk1',
            'dkk2',
            'sl_k', 
            'it_sl',
            ('sl_koef',self.sl_koef_tags),
        )
        self.usl_tags = (
            'idserv',
            'lpu', # self.lpu
            'lpu_1', # ignore
            'podr', # ignore
            'profil',
            'vid_vme',
            'det',
            'date_in',
            'date_out',
            'ds',
            'code_usl',
            'kol_usl', 
            'tarif',
            'sumv_usl',
            'prvs',
            'code_md',
            'npl', #ignore
        )
        
        self.sl_tags = (
            'sl_id', #self
            'lpu_1', #data.lpu_1 # ignore yet
            'podr', #data.podr # ignore yet
            'profil', # data.profil
            'profil_k', #tal.prof_k # ignore yet
            'det', #ignore
            'p_cel', # self.p_cel
            'nhistory', #data.nhistory
            'p_per', # DS later
            'date_1', #data.date_1
            'date_2', #data.date_2
            'kd', #DS
            'ds0', # ignore
            'ds1', # data.ds1
            'ds2', # data.ds2
            'c_zab' # self.c_zab
            'dn',	# ignore
            'code_mes1', #ignore
            'code_mes2', #ignore
            #('ksg_kpg', self.ksg_tag),# ignore yet
            'reab', #ignore
            'prvs', #data.prvs
            'vers_spec', 
            'iddokt', #data
            'ed_col', # ignore
            'tarif',  # ignore
            'sum_m',
            ('usl', self.usl_tags, 'list') # list with objects
        )
        self.z_sl_tags = (
            'idcase', #tal.tal_num
            'usl_ok', #tal.usl_ok
            'vidpom', #vidpom
            'for_pom', #tal.for_pom
            'npr_mo', #tal.npr_mo
            'npr_date', #tal.npr_date
            'lpu', #self.lpu
            'date_z_1', #tal.open_date
            'date_z_2', #tal.close_date
            'kd_z', #tal. # just ignore yet
            'vnov_m', #ignore
            'rslt', #tal.rslt
            'ishod', #tal.ishod
            'os_sluch', # self.os_sluch
            'vb_p', # ignore
            ('sl', self.sl_tags), # tuple
            'idsp', #self.idsp
            'sumv', #self.sumv
        )
        self.zap_tags= (
            'n_zap',  # tal.tal_num
            'pr_nov',  # self.pr_nov
            ('pacient', self.pacient_tags),  # tuple
            ('z_sl', self.z_sl_tags)
        )
        self.zap = ('ZAP', self.zap_tags)

        self.ignore = (
            # Pacient
            'inv',  # ignore
            'mse',  # ignore
            'vnov_d',  # ignore

            # Z_sl
            'kd_z',  # tal. # just ignore yet
            'vnov_m',  # ignore
            'vb_p',  # ignore

            # Sl
            'lpu_1',  # data.lpu_1 # ignore yet
            #'podr',  # data.podr # ignore yet
            # Sl DS
            'profil_k',  # tal.prof_k # ignore yet
            'p_per',  # DS later
            'kd',  # DS
            'dn',  # ignore
            'ksg_kpg',  # ignore yet

            'code_mes1',  # ignore
            'code_mes2',  # ignore
            'reab',  # ignore

            'ed_col',  # ignore
            'tarif',  # ignore


       )
        self.required= (
            # Zap
            'n_zap',
            'pr_nov',

            # Pacient
            'id_pac',  # tal.crd_num
            'vpolis',  # crd.polis_type
            'npolis',  # crd.polis_num
            'novor',

            # Z_sl
            'idcase',
            'usl_ok',
            'vidpom',
            'for_pom',
            'lpu',
            'date_z_1',
            'date_z_2',
            'rslt',
            'ishod',
            'idsp',
            'sumv',

            # Sl
            'sl_id',
            'profil',
            'det',
            'nhistory',
            'date_1',
            'date_2',
            'prvs',
            'vers_spec',
            'iddokt',
            'sum_m',


        )
        self.cnt=(
            'idserv',
        )
        self.list_tags=(
            'usl',
        )

    def get_sumv_usl(self, code_usl, kolvo):
        kol = kolvo
        kol = 1
        return self.tarifs.vzaimo_pmu.get(code_usl, [0.00])[0] * kol
    
    def get_sumv_stom(self, code_usl, kolvo):
        kol = kolvo
        kol = 1
        stom_base = self.tarifs.gonorar[85][0]
        return self.tarifs.stom_pmu.get(code_usl, [0.00])[0] * kol * stom_base
            
    def set_usl(self, tag, usl_list, usp, data, stom=False):
        sum = 0.0
        if not isinstance(usl_list, list):
            _list = [ usl_list ]
        else:
             _list = usl_list
        u_list = []
        for _usl in _list:
            usl = HmUsl(self.mo, _usl, data)
            sum += _usl.sumv_usl
            """
            if stom:
                setattr(usl, 'sumv_usl', '%.2f' % self.get_sumv_stom(usl.code_usl, usl.kol_usl ) )
            else:
                setattr(usl, 'sumv_usl', '%.2f' % self.get_sumv_usl(usl.code_usl, usl.kol_usl) )
        """
            u_list.append(usl)
        u_list.append( HmUsp(self.mo, usp, data) )
        setattr(self, tag, u_list)

        if self.tariff is not None:
            sum += self.tariff
            setattr(self, 'tarif', '{0:.2f}'.format(self.tariff))

        summ = '{0:.2f}'.format(sum)
        setattr(self, 'sum_m', summ)
        setattr(self, 'sumv', summ)
        return self
    
    def set_ksg(self, n_ksg):
        setattr(self.ksg_class_inst, 'n_ksg', n_ksg)
        setattr(self.ksg_class_inst, 'koef_z', self.tarifs.ksg[n_ksg][0])
        setattr(self.ksg_class_inst, 'bztsz', self.tarifs.base['KSG'][0])
        setattr(self.ksg_class_inst, 'koef_d', self.tarifs.ksg[n_ksg][2])
        setattr(self.ksg_class_inst, 'koef_u', self.tarifs.ksg[n_ksg][3])
        self.ksg_kpg = [self.ksg_class_inst]
    
    def reset_ksg(self):
        self.ksg_kpg = None
    
    def get_zap(self, data):

        """
        kdz = data.visit_hs + data.visit_ds
        if kdz > 0:
            setattr(data, 'kd_z', int(kdz))
            setattr(data, 'kd', int(kdz))
        else:
            setattr(data, 'kd_z', None)
            setattr(data, 'kd', None)
        """
        #self.pacient = [data]
        #self.z_sl = self.pacient
        #self.sl = self.pacient


        #return self.wrap_tags( self.zap[0], self.zap[1:], data)
        return self.make_el( self.zap, data)

    def close(self): pass
        #self.tarifs.close()
        #self.tdb.close()