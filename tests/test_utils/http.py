# coding: utf-8

from future.standard_library import install_aliases
install_aliases()
from urllib.parse import unquote


def parse_body(body):
    decoded_body = unquote(body)
    lines = decoded_body.split('&')
    ret = dict()
    for line in lines:
        parts = line.split('=')
        ret[parts[0]] = parts[1]
    return ret
