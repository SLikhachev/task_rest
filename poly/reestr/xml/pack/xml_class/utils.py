import xml.etree.cElementTree as ET


# XRAY, UZI, ENDOSC, LABGEN, GISTOL
USL_PROF = (78, 106, 123, 40, 15)
USL_SPEC = (63, 10, 85,)
USL_PRVS = (60, 81, 93, 31, 48)
USL_PURP = (4,)
PROFOSM_PURP = (21, 22)
STOM_PROF = (85, 86, 87, 88, 89, 90)
SESTRY_PROF = (82, 83)
REGION = '250'


class DataObject:

    def __init__(self, ntuple):

        for name, value in ntuple._asdict().items():
            setattr(self, name, value)

    def fmt_000(self, val):
        if val is None:
            return ''
        v = int(val)
        s = "{0:03d}".format(v)
        if len(s) > 3:
            return s[-3:]
        return s


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
