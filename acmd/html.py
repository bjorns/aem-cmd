# coding: utf-8

from xml.dom import minidom

def _split(attr):
    if '=' in attr:
        ret = attr.split('=')
        return ret[0], ret[1]
    else:
        return 'id', attr

def parse_value(src, node_name, attr):
    attr_name,attr_val = _split(attr)

    doc = minidom.parseString(src)
    for elem in doc.getElementsByTagName(node_name):
        if elem.attributes.get(attr_name) and \
            elem.attributes.get(attr_name).value == attr_val:
            return elem.childNodes[0].nodeValue
    raise Exception("Failed to locate path in {}".format(text))
