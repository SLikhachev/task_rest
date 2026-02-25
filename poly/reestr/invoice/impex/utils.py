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


def tmp_table_name() -> sql.Identifier:
    """
    Return a random alhpa-num string, used as tail of the file name.

    This string is used as a table name in the database.
    """
    return sql.Identifier(f'az{get_name_tail(10)}')
