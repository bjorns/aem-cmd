# coding: utf-8
""" Campatibility layer to make python2 & 3 support easier

Python 3 changes the default str type to unicode
This causes issues when we need specifically a bytearray
e.g. at encryption time

At the same time we try to keep string
remaining in the environment default mode to
reduce friction and surprise for developers.
"""
import sys

# The availability of crypto libraries is weird
# Enable backup
try:
    from Crypto import Random as _Random
    from Crypto.Cipher import AES as _AES
except:
    try:
        from Cryptodome.Cipher import AES as _AES
        from Cryptodome import Random as _Random
    except:
        _AES = None
        _Random = None


class CryptoComaptLayer(object):
    def __init__(self, random, aes):
        self.Random = random
        self.AES = aes

    def is_supported(self):
        return (self.Random is not None) and (self.AES is not None)


crypto = CryptoComaptLayer(_Random, _AES)


def bytestring(string):
    """ Let both python 2 and 3 remain in their default string types.
        :return str|bytes
    """
    if running_python3():
        if type(string) == bytes:
            return string
        return string.encode('utf-8')
    else:
        return string


def stdstring(data):
    """ Let both python 2 and 3 remain in their default string types
        Convert bytestrings to default environment string type.
        :return str
    """
    if running_python3():
        if type(data) == bytes:
            return data.decode('utf-8')
    else:
        if type(data) == unicode:
            return data.encode('utf-8')

    return data


def running_python3():
    """ :return True if python version is >= 3.0 """
    return sys.version_info[0] >= 3
