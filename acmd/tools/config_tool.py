# coding: utf-8
import optparse
import os
import os.path

from configparser import ConfigParser

import acmd
import acmd.util.crypto
from acmd import OK, USER_ERROR, tool, error
from acmd.compat import stdstring
from acmd.config import is_encrypted
from acmd.util.crypto import parse_prop, encode_prop, encrypt_str, decrypt, IV_BLOCK_SIZE, SALT_BLOCK_SIZE, get_key
from .tool_utils import get_argument, get_action

PASSWORD_PROP = 'password'

parser = optparse.OptionParser("acmd config <format|encrypt|decrypt> [options] <file>")
parser.add_option("-f", "--file", dest="rcfile", help="The config file to process")


@tool('config')
class ConfigTool(object):
    """ Manage config file and passwords. """

    def __init__(self):
        pass

    @staticmethod
    def execute(_, argv):
        options, args = parser.parse_args(argv)

        action = get_action(args)
        server_name = get_argument(args)

        if server_name == '':
            error("Missing server name argument")
            return USER_ERROR

        filename = options.rcfile or acmd.get_rcfilename()

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

        if action == 'format':
            return format_config(filename)
        if action == 'encrypt':
            return encrypt_config(server_name, filename)
        if action == 'decrypt':
            return decrypt_config(server_name, filename)
        else:
            error("Unknown command '{}'".format(action))
            return USER_ERROR


def format_config(filename):
    """ Parse and then write the config back out again. """
    config = read_config(filename)

    with open(filename, 'w') as f:
        config.write(f, space_around_delimiters=True)

    return OK


def decrypt_config(server_name, filename):
    """ Decrypt password in config. """
    config = read_config(filename)
    section_name = 'server {}'.format(server_name)
    prop = config.get(section_name, PASSWORD_PROP)

    if not is_encrypted(prop):
        error("Password for server {} is not encrypted".format(server_name))
        return USER_ERROR
    iv_bytes, key_salt, ciphertext_bytes, = parse_prop(prop)

    key_bytes = get_key(key_salt, "Passphrase: ")
    assert type(key_bytes) == bytes

    msg = decrypt(iv_bytes, key_bytes, ciphertext_bytes)
    if msg[0] != '[' or msg[-1] != ']':
        error("Passphrase incorrect")
        return USER_ERROR
    plaintext_password = msg[1:-1]
    config.set(section_name, PASSWORD_PROP, plaintext_password)

    with open(filename, 'w') as f:
        config.write(f)
    return OK


def encrypt_config(server_name, filename):
    """ Encrypt given server password. """
    config = read_config(filename)
    section_name = 'server {}'.format(server_name)

    if not config.has_section(section_name):
        error("No section {} in config {}".format(server_name, filename))
        return USER_ERROR

    plaintext_password = stdstring(config.get(section_name, PASSWORD_PROP))
    assert type(plaintext_password) == str

    if is_encrypted(plaintext_password):
        error("Password for server {} is already encrypted".format(server_name))
        return USER_ERROR

    # Put fixes on string to be able to recognize successful decryption
    formatted_password = "[" + plaintext_password + "]"

    iv_bytes = acmd.util.crypto.random_bytes(IV_BLOCK_SIZE)
    assert type(iv_bytes) == bytes  # get_iv() is sometimes mocked and should be checked in tests

    key_salt = acmd.util.crypto.random_bytes(SALT_BLOCK_SIZE)
    key_bytes = get_key(key_salt, "Set passphrase: ")

    ciphertext_bytes = encrypt_str(iv_bytes, key_bytes, formatted_password)

    prop = encode_prop(iv_bytes, key_salt, ciphertext_bytes)

    config.set(section_name, PASSWORD_PROP, prop)
    with open(filename, 'w') as f:
        config.write(f)
    return OK


def read_config(filename):
    """ Read config file and return config object. """
    config_parser = ConfigParser()
    with open(filename, 'r') as f:
        config_parser.read_file(f)
    return config_parser
