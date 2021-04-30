# import xml.etree.cElementTree as ET
import re

# XRAY, UZI, ENDOSC, LABGEN, GISTOL
USL_PROF = (78, 106, 123, 40, 15)
USL_SPEC = (63, 10, 85,)
USL_PRVS = (60, 81, 93, 31, 48)
USL_PURP = (4,)
PROFOSM_PURP = (21, 22)
STOM_PROF = (85, 86, 87, 88, 89, 90)
SESTRY_PROF = (82, 83)
REGION = '250'
ED_COL_IDSP = (25, 28, 29)

class FormatVal:

    def fmt_000(self, val):
        if val is None:
            return ''
        v = int(val)
        s = "{0:03d}".format(v)
        if len(s) > 3:
            return s[-3:]
        return s


class DataObject(FormatVal):

    def __init__(self, ntuple, mo, napr_mo=None):

        for name, value in ntuple._asdict().items():
            setattr(self, name, value)
        # for chck
        self.mo = mo  # str(3) 228
        self.npr_mo = napr_mo  # str(6) 250228
        if not hasattr(self, 'mo_att'):
            self.mo_att = None

        id = f'{self.idcase}'

        self.check = (
            self._date,
            self._smo_polis,
            self._purp,
            self._visits,
            self._naprav_cons,
            self._naprav_hosp,
            self._ds,
            self._doct,
            self._pacient

        )

        for func in self.check:
            func(id)

    def _date(self, id):
        '''
            tal.open_date as date_1,
            tal.close_date as date_2,
            tal.crd_num as card,
        '''
        assert self.date_1 and self.date_2, f'{id}-Нет даты талона'
        assert self.date_2 >= self.date_1, f'{id}-Дата 1 больше даты 2'
        assert self.card, f'{id}-Нет карты талона'

    def _smo_polis(self, id):
        '''
            tal.mek, -- as pr_nov,

            tal.smo as tal_smo,
            tal.polis_type,
            tal.polis_ser,
            tal.polis_num,
            tal.smo_okato,

            crd.smo as smo,
            crd.polis_type as vpolis,
            crd.polis_num as npolis,
            crd.polis_num as id_pac,
            crd.polis_ser as spolis,
            crd.st_okato,
            crd.smo_ogrn,
            crd.smo_okato as smo_ok,
            crd.smo_name as smo_nam,
        '''
        self.pr_nov = 1 if bool(self.mek) else 0

       # set smo, polis from talon
        if self.polis_type is not None and self.polis_num is not None:

            self.vpolis = self.polis_type
            self.npolis = self.polis_num
            self.spolis = self.polis_ser
            self.smo = self.tal_smo
            self.smo_ok = self.smo_okato
            self.id_pac = self.polis_num

        assert self.vpolis, f'{id}-Тип полиса не указан'
        assert self.npolis, f'{id}-Номер полиса не указан'
        if self.vpolis == 1:
            assert self.spolis and self.npolis, f'{id}-Тип полиса не соответвует типу 1 (старый)'
        elif self.vpolis == 2:
            assert len(
                self.npolis) < 16, f'{id}-Тип полис не времянка, не соответвует типу 2'
        elif self.vpolis == 3:
            assert len(
                self.npolis) == 16, f'{id}-Тип полис не ЕНП, не соответвует типу 3'
        else:
            raise AttributeError(f'{id}-Тип полиса не поддерживаем')
        if not bool(self.smo):
            self.smo = None
        assert self.smo or self.smo_ok, f'{id}-Нет ни СМО ни СМО ОКАТО'

        try:
            self.id_pac = int(self.id_pac)
        except ValueError:
            raise ValueError(f'{id}-Номер полиса не целое число')

    def _purp(self, id):
        '''
            tal.doc_spec as specfic,

            tal.purp,
            tal.usl_ok,
            tal.for_pom,
            tal.rslt,
            tal.ishod,
        '''
        # assert self.specfic, f'{id}-SPECFIC ( специальность из регионального справочника) не указан'
        if not self.purp:
            self.purp = -2  # for usk_ok=2
        assert self.usl_ok, f'{id}-USL_OK (условия оказания) не указан'
        assert self.for_pom, f'{id}-FOR_POM (форма помощи) не указан'
        assert self.rslt and self.ishod, f'{id}-RESULT/ISHOD (исход, результат) не указан'

    def _visits(self, id):
        '''
            tal.visit_pol, 
            tal.visit_home as visit_hom,
        '''
        assert self.visit_pol, f'{id}-Нуль количество посещений АПП'  # yet

    # приняли на консультацию
    def _naprav_cons(self, id):
        '''
            tal.npr_date,
            tal.npr_mo as cons_mo,
            tal.hosp_mo,
            tal.naprlech,
            tal.nsndhosp,
            tal.d_type,
        '''
    # diagnostic
        if (self.prvs in USL_PRVS) and (self.for_pom != 2):
            if self.mo_att != self.mo:
                assert bool(self.naprlech) and bool(
                    self.npr_mo), f'{id}-Диагностика, нет прикрепления, напаравления, МО направления'
            else:
                # diagnostic in self MO
                self.npr_mo = f'{REGION}{self.mo}'
                self.npr_date = self.date_1
                self.from_firm = None
                self.naprlech = None

        if bool(self.naprlech):
            assert bool(self.npr_mo), f'{id}-Нет МО направления NPR_MO'
            self.npr_date = self.date_1
            self.from_firm = self.fmt_000(self.npr_mo)

    def _naprav_hosp(self, id):
        '''
            tal.npr_date,
            tal.npr_mo as cons_mo,
            tal.hosp_mo,
            tal.naprlech,
            tal.nsndhosp,
            tal.d_type,
        '''
        # hospital from self MO
        if bool(self.nsndhosp):
            self.from_firm = self.mo

    def _ds(self, id):
        '''
            tal.d_type,
            tal.ds1,
            tal.ds2,
            tal.char1 as c_zab,
        '''

        assert self.ds1, f'{id}-Нет DS1 (основной диагноз)'
        if self.ds1.upper().startswith('Z'):
            self.c_zab = None
        else:
            assert self.c_zab, f'{id}-Нет C_ZAB (характер основного заболевания)'

    def _doct(self, id):
        """
            spec.prvs,
            spec.profil,
            doc.snils as iddokt,
        """
        assert self.prvs and self.profil, f'{id}-Нет PRVS | PROFIL (кода специальности по V021, профиля V002)'
        assert self.iddokt, f'{id}-Нет СНИЛС у доктора'
        assert (self.prvs in USL_PRVS) and (self.purp in USL_PURP), \
            f'{id}-Для спец. {self.specfic}, prvs {self.prvs} неверная цель - {self.purp}'

        #self.iddokt = self.iddokt.replace(" ", "-")

        # 2020 FOMS 495 letter
        if (self.prvs in USL_PRVS) and (self.for_pom != 2):
            self.ishod = 4  # 304
            self.rslt = 14  # 314

        self.ishod += self.usl_ok * 100
        self.rslt += self.usl_ok * 100

    def _pacient(self, id):
        '''    
        -- PACIENT
            crd.fam, 
            crd.im,
            crd.ot,
            crd.gender as pol,
            crd.birth_date as dr,
            crd.dost as dost,
            crd.dul_type as doctype,
            crd.dul_serial as docser,
            crd.dul_number as docnum,
            crd.dul_date as docdate,
            crd.dul_org as docorg
        '''
        
        assert self.fam, f'{id}-Нет Фамилии пациента'
        assert self.dr, f'{id}-Нет дня рождения пациента'
        if self.vpolis != 3:
            #print(self.doctype, self.docser, self.docnum)
            assert self.doctype and self.docnum and self.docser and \
                self.docdate and self.docorg, \
                    f'{id}-Тип полиса не ЕНП и неуказан полностью ДУЛ'
            if self.doctype and self.doctype == 14: # pass RF
                assert re.fullmatch('^\d\d \d\d$', self.docser), \
                    f'{id}-Серия паспрота не в формате 99 99: {self.docser}'
                assert re.fullmatch('^\d{6}$', self.docnum), \
                    f'{id}-Номер паспорта не 6 цифр'
        
        # local person no doc_date doc_org needed
        if bool(self.smo):
             self.docdate, self.docorg = None, None
        # self.os_sluch= 2 if self.dost.find('1') > 0 else None


'''
class DictView(object):
    def __init__(self, d):
        self.__dict__ = d


class DictObject(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)


class Leaf:

    __slots__ = ('tag')

    def __init__(self, name, value):
        self.tag = self.et(name, value)

    def et(self, n, v):
        e = ET.Element(self.tag.upper())
        e.text = f'{v}'
        return e


class Node:

    __slots__ = ('root', 'children')

    def __init__(self, root, childern):
        self.root = None
        self.children = None
'''
