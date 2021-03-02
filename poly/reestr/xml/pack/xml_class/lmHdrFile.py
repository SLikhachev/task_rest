
from poly.reestr.xml.pack.xml_class.mixTags import HdrMix, TagMix
from poly.reestr.xml.pack.xml_class.utils import DataObject


def lmData(data):

    def _pol(data):
        try:
            return ('w', ['м', 'ж'].index(data.pol.lower()) + 1)
        except Exception as e:
            print(e)
            raise e

    def _dost(data):
        dost = []
        if not bool(data.ot):
            dost.append(1)
        if not bool(data.fam):
            dost.append(2)
        if not (data.im):
            dost.append(3)
        return ('dost', dost)

    def _doc(data):
        if not bool(data.docnum) or len(data.docnum) == 0:
            for d in ('doctype', 'docnum', 'docser', 'docdate', 'docorg',):
                setattr(data, d, None)
        return None

    calc = (
        _pol,
        _dost,
        _doc
    )

    for func in calc:
        t = func(data)
        if t is None:
            continue
        setattr(data, t[0], t[1])

    return data


class LmHdr(HdrMix):

    def __init__(self, mo, year, month, pack, sd_z=None, summ=None):
        super().__init__(mo, year, month, pack)
        self.startTag = '%s\n<PERS_LIST>' % self.xmlVer
        self.endTag = '</PERS_LIST>'
        self.filename = self.l_file
        self.filename1 = self.h_file
        self.version = '3.2'

        self.zglv_tags = (
            'version',
            'data',
            'filename',
            'filename1',
        )
        self.zglv = ('ZGLV', self.zglv_tags)

    def get_schet(self, data):
        return None


class LmPers(TagMix):

    def __init__(self, mo):
        super().__init__(mo)
        self.dubl = []
        self.uniq = set()
        self.pers_tags = (
            'id_pac',
            'fam',
            'im',
            'ot',
            'w',
            'dr',
            'dost',
            'tel',
            'fam_p',
            'im_p',
            'ot_p',
            'w_p',
            'dr_p',
            'dost_p',
            'mr',
            'doctype',
            'docser',
            'docnum',
             #'docdate',
             #'docorg',
            'snils',
            'okatog',
            'okatop',
            'commentp',
        )
        self.ignore = (
            'mr',
            'snils',
            'okatog',
            'okatop',
            'commentp',
        )
        self.pers = ('pers', self.pers_tags)

    def get_pers(self, data):

        if data.id_pac in self.uniq:
            self.dubl.append(data.id_pac)
            return None

        self.uniq.add(data.id_pac)
        return self.make_el(self.pers, data)
