# coding: utf-8
import sys
import os.path
import optparse
import json

import requests

from acmd import tool, log
from acmd import OK, SERVER_ERROR, USER_ERROR
from acmd.props import parse_properties

parser = optparse.OptionParser("acmd assets <import|touch> [options] <file>")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")


@tool('assets')
class AssetsTool(object):
    """ Manage AEM DAM assets """

    @staticmethod
    def execute(server, argv):
        options, args = parser.parse_args(argv)

        return OK


def import_file(server, options, filename):
    pass
