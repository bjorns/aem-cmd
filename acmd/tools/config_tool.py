# coding: utf-8
import getpass
import hashlib
import optparse
import os

from configparser import ConfigParser

from acmd import OK, USER_ERROR, tool, error
from acmd.compat import bytestring, stdstring
from acmd.util.crypto import parse_prop, encode_prop, encrypt_str, decrypt_str
import acmd.util.crypto

from .tool_utils import get_argument, get_action

PASSWORD_PROP = "password"

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


def is_encrypted(password):
    return password.startswith('{') and password.endswith('}')


def decrypt_config(server, filename):
    config = read_config(filename)
    section_name = 'server {}'.format(server.name)
    prop = config.get(section_name, PASSWORD_PROP)

    if not is_encrypted(prop):
        error("Password for server {} is not encrypted".format(server.name))
        return USER_ERROR
    encrypted_password, iv = parse_prop(prop)

    key = get_key(iv, "Passphrase: ")

    msg = decrypt_str(iv, key, encrypted_password)
    if msg[0] != '[' or msg[-1] != ']':
        error("Passphrase incorrect")
        return USER_ERROR
    plaintext_password = msg[1:-1]
    config.set(section_name, PASSWORD_PROP, plaintext_password)

    with open(filename, 'w') as f:
        config.write(f)
    return OK


def encrypt_config(server, filename):
    config = read_config(filename)
    section_name = 'server {}'.format(server.name)
    plaintext_password = stdstring(config.get(section_name, PASSWORD_PROP))
    assert type(plaintext_password) == str

    if is_encrypted(plaintext_password):
        error("Password for server {} is already encrypted".format(server.name))
        return USER_ERROR

    # Put fixes on string to be able to recognize successful decryption
    formatted_password = "[" + plaintext_password + "]"
    iv_bytes = acmd.util.crypto.generate_iv()
    assert type(iv_bytes) == bytes  # get_iv() is sometimes mocked and should be checked in tests

    # TODO: Not sure reusing IV for key generation is a good idea
    key = get_key(iv_bytes, "Set passphrase: ")

    encrypted_password = encrypt_str(iv_bytes, key, formatted_password)

    prop = encode_prop(encrypted_password, iv_bytes)

    config.set(section_name, PASSWORD_PROP, prop)
    with open(filename, 'w') as f:
        config.write(f)
    return OK


def get_key(salt, message):
    passphrase = getpass.getpass(message)
    dk = hashlib.pbkdf2_hmac('sha256', bytestring(passphrase), bytestring(salt), 100000)
    return dk


def read_config(filename):
    config_parser = ConfigParser()
    with open(filename, 'r') as f:
        config_parser.read_file(f)
    return config_parser
