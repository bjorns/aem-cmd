# coding: utf-8
""" Tools for bash command completion are hidden from normal listings. """
import sys
import optparse

from acmd import tool, get_current_config, OK
from acmd import get_tool
from acmd import list_tools
from acmd import error, USER_ERROR
from acmd.config import DEFAULT_SERVER_SETTING
from acmd.tools import get_command

parser = optparse.OptionParser("acmd bundle [options] [list|start|stop] [<bundle>]")
parser.add_option("-c", "--compact",
                  action="store_const", const=True, dest="compact",
                  help="output compact lists useful for completion")


@tool('help')
class IntrospectTool(object):
    @property
    def commands(self):
        """ Allow autocomplete of help tools. """
        return list_tools()

    def execute(self, _, argv):
        (options, args) = parser.parse_args(argv)

        arg = get_command(args, '_tools')
        if arg == '_tools':
            print_tools(sys.stdout, options.compact)
        elif arg == '_servers':
            print_servers(sys.stdout)
        else:
            _tool = get_tool(arg)
            if _tool is None:
                error("No tool named {} found".format(arg))
                print_tools(sys.stderr, options.compact)
                return USER_ERROR
            if options.compact:
                for cmd in _tool.commands:
                    sys.stdout.write("{}\n".format(cmd))
            else:
                sys.stdout.write("Available commands:\n")
                for cmd in _tool.commands:
                    sys.stdout.write("    {}\n".format(cmd))
            return OK


def print_servers(f):
    config = get_current_config()
    for name, _ in config.servers.items():
        if name != DEFAULT_SERVER_SETTING:
            f.write("{}\n".format(name))


def print_tools(f, compact):
    if compact:
        for arg in list_tools():
            f.write("{cmd}\n".format(cmd=arg))
    else:
        sys.stdout.write("Available tools:\n")
        for arg in list_tools():
            f.write("    {cmd}\n".format(cmd=arg))
