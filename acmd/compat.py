# coding: utf-8
""" Campatibility layer to make python2 & 3 support easier
"""
import sys

try:
    from Crypto import Random as _Random
    from Crypto.Cipher import AES as _AES
except:
    from Cryptodome.Cipher import AES as _AES
    from Cryptodome import Random as _Random

Random = _Random
AES = _AES


def bytestring(string):
    """ Let both python 2 and 3 remain in their default string types. """
    if running_python3():
        if type(string) == bytes:
            return string
        return string.encode('utf-8')
    else:
        return string


def stdstring(data):
    """ Let both python 2 and 3 remain in their default string types. """
    if running_python3():
        if type(data) == bytes:
            return data.decode('utf-8')
    else:
        if type(data) == unicode:
            return data.encode('utf-8')

    return data


def running_python3():
    return sys.version_info[0] >= 3
