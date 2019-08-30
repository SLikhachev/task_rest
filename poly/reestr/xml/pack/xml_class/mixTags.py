
import xml.etree.cElementTree as ET
from datetime import date


class TagMix:
    
    '''
    def __getattr__(self, name):
        if name in self.__dict__.keys():
            return self.__dict__[name]
        else:
            raise AttributeError("No such attribute: " + name)
    '''
    
    def __init__(self, mo):
        self.mo = mo
        self.lpu= f"250{mo}"
        self.next= 0
        self.ignore = tuple()
        self.required = tuple()
        self.cnt = tuple()
        self.calc = tuple()
        self.zglv= None
        self.schet= None


    def fmt_000(self, val):
        s = "{0:03d}".format(val)
        if len(s) > 3: return s[-3:]
        return s
    
    def non_zero(self, val):
        try:
            if int(val) == 0:
                return None
            return int(val)
        except Exception as e:
            print(e)
            return None
    
    def id(self, val):
        return val
    
    def next_item(self):
        self.next += 1
        return self.next

    def next_init(self, val):
        self.next = val
    
    def el(self, tag, val):
        if val is None:
            return None
        e = ET.Element(tag.upper())
        e.text = '%s' % val
        return e

    def _els(self, tag, obj):
        # composed tags
        if isinstance(tag, tuple):
            if len(tag) > 2:
                return self.make_els(tag[0:2], self)  # return an [ET.Element]
            return [ self.make_el(tag, obj) ]
        #simple tag
        # ignore tag
        if tag in self.ignore:
            return None
        # just leaf tag
        # get value from database object
        val = getattr(obj, tag, None)
        # print(val)
        if val is None:
            val = getattr(self, tag, None)
            if val is None:
                if tag in self.cnt:
                    val = self.next_item()
                elif tag in self.required:
                    raise AttributeError(f'Absent required Tag {tag}')
                else:
                    return None

        # many same tags with differnet text value
        if isinstance(val, list):
            return [self.el(tag, v) for v in val]
        else:
            return [self.el(tag, val)]

    def make_el(self, tags, obj):
        root, body = tags
        proot = ET.Element(root.upper())
        for tag in body:
            els = self._els(tag, obj)
            if els is None:
                continue
            for el in els:
                proot.append(el)

        return proot

    def make_els(self, tags, obj):
         elems = getattr(obj, tags[0], None)
         if elems is None:
             return None
         # print(root, elems)
         self.next_init(0)
         return [self.make_el(tags, el) for el in elems]

    def get_zag(self, data):
        return self.make_el( self.zglv, data )
    
    def get_schet(self, data):
         return self.make_el( self.schet, data )


class HdrMix(TagMix):
    
    def __init__(self, mo, year, month, pack):
        super().__init__(mo)
        self.xmlVer= '<?xml version="1.0" encoding="windows-1251"?>'
        self.version = '3.1'
        self.lpu= mo
        self.year= f'{year}'
        self.month= month
        self.pack= int(pack)
        self.pack_num= "{0:02d}".format( self.pack )
        self.code_mo= '250%s' % mo
        self.startTag = '%s\n<ZL_LIST>' % self.xmlVer
        self.endTag = '\n</ZL_LIST>'
        self.data = date.today().isoformat()
        self.file = f'M{self.code_mo}T25_{self.year[2:]}{month}{mo}{self.pack}.xml'
        self.p_file= f'P{self.file}'
        self.h_file= f'H{self.file}'
        self.l_file= f'L{self.file}'
        self.pack_name=f'H{self.code_mo}{self.year[-1]}{month}{self.pack_num}.zip'
        #print(self.year)