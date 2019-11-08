
import xml.etree.cElementTree as ET

def get_text(elem: ET.Element, tag: str) -> str:
    e= elem.find(tag)
    if hasattr(e, 'text'):
        return e.text
    return None
