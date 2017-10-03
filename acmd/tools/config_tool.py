# coding: utf-8
import base64
import optparse
import os
import sys
import getpass
import hashlib, binascii

from Crypto.Cipher import AES

from builtins import input
from configparser import ConfigParser

from acmd import OK, USER_ERROR, tool, error
from acmd.config import parse_server
from .tool_utils import get_argument, get_action

PASSWORD_PROP = 'password'
IV = 'This is an IV456'

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
    ok = False
    while ok is False:
        input_var = input("Rebuild config file {}? any commented out lines will be lost. [yN]: ".format(filename))
        if input_var == 'n' or input_var == '':
            return OK
        ok = (input_var == 'y')

    config = read_config(filename)

    with open(filename, 'w') as f:
        config.write(f, space_around_delimiters=True)

    return OK


def _format_password(encrypted_password):
    return "[{}]".format(encrypted_password)


KEY = 'key_key_key_key_'


def is_encrypted(password):
    return password.startswith('[') and password.endswith(']')


def decrypt_config(server, filename):
    config = read_config(filename)
    section_name = 'server {}'.format(server.name)

    password = config.get(section_name, PASSWORD_PROP)
    if not is_encrypted(password):
        error("Password for server {} is not encrypted".format(server.name))
        return USER_ERROR
    key = get_key("Passphrase: ")
    print("Key: {}".format(base64.b64encode(key)))

    msg = config.get(section_name, PASSWORD_PROP)
    msg = msg[1:-1]  # Remove brackets
    print("Msg: {}".format(msg))
    msg = decrypt_str(key, msg)
    print(msg)


def encrypt_config(server, filename):
    config = read_config(filename)
    section_name = 'server {}'.format(server.name)

    password = config.get(section_name, PASSWORD_PROP)
    print("Password: {}".format(password))
    if is_encrypted(password):
        error("Password for server {} is already encrypted".format(server.name))
        return USER_ERROR

    key = get_key("Set passphrase: ")
    print("Key: {}".format(base64.b64encode(key)))

    encrypted_password = encrypt_str(key, password)
    config.set(section_name, PASSWORD_PROP, _format_password(encrypted_password))

    print(encrypted_password)
    return OK


def get_key(message):
    passphrase = getpass.getpass(message)
    dk = hashlib.pbkdf2_hmac('sha256', passphrase.encode('UTF-8'), b'salt', 100000)
    return dk


def read_config(filename):
    config_parser = ConfigParser()
    with open(filename, 'r') as f:
        config_parser.read_file(f)
    return config_parser


def encrypt_str(key, s):
    codec = AES.new(key, AES.MODE_CFB, IV)
    bindata = codec.encrypt(s)
    return base64.b64encode(bindata)


def decrypt_str(key, s):
    bindata = base64.b64decode(s)
    codec = AES.new(key, AES.MODE_CFB, IV)
    return codec.decrypt(bindata)
