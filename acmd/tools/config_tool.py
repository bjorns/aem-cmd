# coding: utf-8
import optparse
import os
from configparser import ConfigParser
from builtins import input

from acmd import OK, USER_ERROR, tool, error
from .tool_utils import get_argument, get_action

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

    config_parser = ConfigParser()
    with open(filename, 'r') as f:
        config_parser.read_file(f)

    with open(filename, 'w') as f:
        config_parser.write(f, space_around_delimiters=True)

    return OK
