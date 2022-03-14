
from psycopg2 import sql
import xml.etree.cElementTree as ET
from poly.utils.files import get_name_tail


def get_text(elem: ET.Element, tag: str) -> str:
    e= elem.find(tag)
    if hasattr(e, 'text'):
        return e.text
    return None


def tmp_table_name():
    return sql.Identifier(f'az{get_name_tail(10)}')