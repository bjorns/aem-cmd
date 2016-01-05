# coding: utf-8
import re

from acmd import log


def parse_properties(props_str):
    """ Translate command line properties string to dictionary.
            example: prop0=value,prop1="Quoted value"
    """
    log("Parsing props string '{}'".format(props_str))
    ret = dict()
    rest = props_str
    while rest.strip() != '':
        key, val, val_type, rest = _parse_property(rest)
        log("    setting {}={}".format(key, val))
        if val_type is not None:
            ret[_typeof(key)] = val_type
        ret[key] = val
    return ret


def _typeof(key):
    return key + "@TypeHint"


def _parse_property(prop_str):
    key, _, rest = prop_str.partition('=')
    if rest.startswith('"'):
        value, rest = _get_quoted_value(rest)
        val_type = 'String'
    else:
        value, _, rest = rest.partition(',')
        val_type = _infer_type(value)
    return key, value, val_type, rest


def _get_quoted_value(rest):
    rest = rest.lstrip('"')
    parts = re.split(r'(?<!\\)"', rest, maxsplit=1)
    value = parts[0]
    rest = parts[1] if len(parts) > 1 else ""
    rest = rest.lstrip(',')
    return value, rest


def _infer_type(val):
    if val.lower() == 'true' or val.lower() == 'false':
        log("Setting boolean typehint")
        return 'Boolean'
    elif val.isdigit():
        log("Setting integer typehint")
        return 'Long'
    else:
        return None
