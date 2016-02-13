# coding: utf-8
import sys
import optparse
from urlparse import urlparse

import requests

from acmd import tool, log, SERVER_ERROR
from acmd.tools import get_command

parser = optparse.OptionParser("acmd dispatcher [options] [clear]")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")


@tool('dispatcher', ['clear'])
class DispatcherTool(object):
    def execute(self, server, argv):
        (options, args) = parser.parse_args(argv)
        action = get_command(args, 'help')
        if action == 'clear':
            clear_cache(server, options)
        else:
            parser.print_help()


def clear_cache(server, options):
    raise Exception("""The service for clearing dispatcher cache is not safe
        and therefor support has been removed""")
