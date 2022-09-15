""" aux funcs """

from psycopg2 import sql
import xml.etree.cElementTree as ET
from poly.utils.files import get_name_tail

numeric = ['SUMP']

def get_text(elem: ET.Element, tag: str) -> str:
    """ find and return the text node of the tag if any else empty str """
    node= elem.find(tag)
    if hasattr(node, 'text'):
        return node.text
    if tag in numeric:
        return '0.00'
    return ''


def tmp_table_name():
    """ return random alhpa-num string, used as tail of the file name """
    return sql.Identifier(f'az{get_name_tail(10)}')