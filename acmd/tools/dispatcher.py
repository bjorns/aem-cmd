# coding: utf-8
import optparse

from acmd import tool
from acmd.tools import get_command

parser = optparse.OptionParser("acmd dispatcher [options] [clear]")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")


@tool('dispatcher', ['clear'])
class DispatcherTool(object):
    @staticmethod
    def execute(_, argv):
        (options, args) = parser.parse_args(argv)
        action = get_command(args, 'help')
        if action == 'clear':
            clear_cache()
        else:
            parser.print_help()


def clear_cache():
    raise Exception("""The service for clearing dispatcher cache is not safe
        and therefor support has been removed""")
