# coding: utf-8
import urllib


def parse_body(body):
    decoded_body = urllib.unquote(body).decode()

    lines = decoded_body.split('&')
    ret = dict()
    for line in lines:
        parts = line.split('=')
        ret[parts[0]] = parts[1]
    return ret
