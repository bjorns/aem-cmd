# coding: utf-8
""" Tools for bash command completion are hidden from normal listings. """
import optparse
import sys

from acmd import error, USER_ERROR
from acmd import tool, OK
from acmd.config import DEFAULT_SERVER_SETTING
from acmd import tool_repo
from acmd.tools import get_action

parser = optparse.OptionParser("acmd bundle [options] [list|start|stop] [<bundle>]")
parser.add_option("-c", "--compact",
                  action="store_const", const=True, dest="compact",
                  help="output compact lists useful for completion")


@tool('help')
class IntrospectTool(object):
    def __init__(self, config=None):
        self.config = config

    @property
    def commands(self):
        """ Allow autocomplete of help tools. """
        return tool_repo.list_tools()

    @commands.setter
    def commands(self, commands):
        """ Ignore trying to set commands for this tool """
        pass

    def execute(self, _, argv):
        (options, args) = parser.parse_args(argv)

        arg = get_action(args, '_tools')
        if arg == '_tools':
            print_tools(sys.stdout, options.compact)
        elif arg == '_servers':
            print_servers(sys.stdout, self.config)
        else:
            _tool = tool_repo.get_tool(arg)
            _module = tool_repo.get_module(arg)
            if options.compact:
                for cmd in _tool.commands:
                    sys.stdout.write("{}\n".format(cmd))
            else:
                if hasattr(_module, 'parser'):
                    _module.parser.print_help()
                else:
                    sys.stdout.write("Available commands:\n")
                    for cmd in _tool.commands:
                        sys.stdout.write("\t{}\n".format(cmd))
        return OK


def print_servers(f, config=None):
    if config is None:
        return
    for name, _ in config.servers.items():
        if name != DEFAULT_SERVER_SETTING:
            f.write("{}\n".format(name))


def print_tools(f, compact):
    if compact:
        for arg in tool_repo.list_tools():
            f.write("{cmd}\n".format(cmd=arg))
    else:
        sys.stdout.write("Available tools:\n")
        for arg in tool_repo.list_tools():
            f.write("    {cmd}\n".format(cmd=arg))
