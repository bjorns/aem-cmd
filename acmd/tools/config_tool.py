# coding: utf-8
import base64
import getpass
import hashlib
import optparse
import os
import sys

try:
    from Crypto import Random
    from Crypto.Cipher import AES
except:
    from Cryptodome.Cipher import AES
    from Cryptodome import Random

from builtins import input
from configparser import ConfigParser

from acmd import OK, USER_ERROR, tool, error
from .tool_utils import get_argument, get_action

IV_BLOCK_SIZE = 16
PASSWORD_PROP = "password"
PASSWORD_IV_PROP = "password_iv"
PYTHON_3 = 3

parser = optparse.OptionParser("acmd config <rebuild|encrypt|decrypt> [options] <file>")


@tool('config')
class AssetTool(object):
    """ Manage AEM DAM assets """

    def __init__(self):
        pass

    @staticmethod
    def execute(server, argv):
        options, args = parser.parse_args(argv)

        action = get_action(args)
        filename = get_argument(args)

        if filename == '':
            error("Missing filename argument")
            return USER_ERROR

        if not os.path.isfile(filename):
            error("Requested file {} does not exist".format(filename))
            return USER_ERROR
        if not os.access(filename, os.R_OK):
            error("Requested file {} lacks read access".format(filename))
            return USER_ERROR
        if not os.access(filename, os.W_OK):
            error("Requested file {} lacks write access".format(filename))
            return USER_ERROR

        if action == 'rebuild':
            return rebuild_config(filename)
        if action == 'encrypt':
            return encrypt_config(server, filename)
        if action == 'decrypt':
            return decrypt_config(server, filename)
        else:
            error("Unknown command '{}'".format(action))
            return USER_ERROR


def rebuild_config(filename):
    config = read_config(filename)

    with open(filename, 'w') as f:
        config.write(f, space_around_delimiters=True)

    return OK


def _format_password(encrypted_password):
    return "[{}]".format(encrypted_password)


def is_encrypted(password):
    return password.startswith('[') and password.endswith(']')


def decrypt_config(server, filename):
    config = read_config(filename)
    section_name = 'server {}'.format(server.name)
    password = config.get(section_name, PASSWORD_PROP)
    iv = base64.b64decode(config.get(section_name, PASSWORD_IV_PROP))

    if not is_encrypted(password):
        error("Password for server {} is not encrypted".format(server.name))
        return USER_ERROR
    key = get_key("Passphrase: ")
    msg = config.get(section_name, PASSWORD_PROP)
    msg = msg[1:-1]  # Remove brackets
    msg = decrypt_str(iv, key, msg)
    if msg[0] != '_' or msg[-1] != '_':
        error("Passphrase incorrect")
        return USER_ERROR
    plaintext_password = msg[1:-1]
    config.set(section_name, PASSWORD_PROP, plaintext_password)
    config.remove_option(section_name, PASSWORD_IV_PROP)
    with open(filename, 'w') as f:
        config.write(f)
    return OK


def encrypt_config(server, filename):
    config = read_config(filename)
    section_name = 'server {}'.format(server.name)
    plaintext_password = config.get(section_name, PASSWORD_PROP)

    if is_encrypted(plaintext_password):
        error("Password for server {} is already encrypted".format(server.name))
        return USER_ERROR

    # Put fixes on string to be able to recognize successful decryption
    formatted_password = "_{}_".format(plaintext_password)

    key = get_key("Set passphrase: ")

    iv = get_iv()
    encrypted_password = encrypt_str(iv, key, formatted_password)
    config.set(section_name, PASSWORD_PROP, _format_password(encrypted_password))
    config.set(section_name, PASSWORD_IV_PROP, defaultstring(base64.b64encode(iv)))
    with open(filename, 'w') as f:
        config.write(f)
    return OK


def get_key(message):
    passphrase = getpass.getpass(message)
    dk = hashlib.pbkdf2_hmac('sha256', bytestring(passphrase), b'salt', 100000)
    return dk


def read_config(filename):
    config_parser = ConfigParser()
    with open(filename, 'r') as f:
        config_parser.read_file(f)
    return config_parser


def encrypt_str(iv, key, plaintext):
    """ Takes strings in and is expected to give strings out.
        All binary string conversion is internal only.

        iv: 16 character standard string
        key: bytes array
        plaintext: standard string
    """
    if iv is None:
        raise Exception("Missing IV")
    if len(iv) != IV_BLOCK_SIZE:
        raise Exception("Bad IV: {}".format(iv))
    if type(key) != bytes:
        raise Exception("Bad key: {}".format(key))
    codec = AES.new(key, AES.MODE_CFB, iv)
    bindata = codec.encrypt(bytestring(plaintext))
    return defaultstring(base64.b64encode(bindata))


def decrypt_str(iv, key, s):
    """ Takes strings in and is expected to give strings out.
        All binary string conversion is internal only. """
    bindata = base64.b64decode(s)
    codec = AES.new(bytestring(key), AES.MODE_CFB, iv)
    return defaultstring(codec.decrypt(bindata))


def bytestring(string):
    """ Let both python 2 and 3 remain in their default string types. """
    if running_python3():
        if type(string) == bytes:
            return string
        return string.encode('utf-8')
    else:
        return string


def defaultstring(string):
    """ Let both python 2 and 3 remain in their default string types. """
    if running_python3():
        return string.decode('utf-8')
    else:
        return string


def running_python3():
    return sys.version_info[0] >= 3


def get_iv():
    """ Generate initial vector for encryption """
    raise Exception("HEJ")
    return Random.new().read(IV_BLOCK_SIZE)
