# coding: utf-8
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse


def parse_body(body):

    decoded_body = urlparse(body).decode()

    lines = decoded_body.split('&')
    ret = dict()
    for line in lines:
        parts = line.split('=')
        ret[parts[0]] = parts[1]
    return ret
