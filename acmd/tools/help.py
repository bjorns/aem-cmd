# coding: utf-8
""" Tools for bash command completion are hidden from normal listings. """
import sys
import optparse

from acmd import tool, list_tools, get_current_config, USER_ERROR
from acmd.config import DEFAULT_SERVER_SETTING
from acmd.tools import tool_utils


parser = optparse.OptionParser("acmd bundle [options] [list|start|stop] [<bundle>]")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")


@tool('help')
class IntrospectTool(object):
    def execute(self, server, argv):
        (options, args) = parser.parse_args(argv)

        cmd = tool_utils.get_action(args, 'tools')
        if cmd == 'tools':
            if options.raw:
                for cmd in list_tools():
                    sys.stdout.write("{cmd}\n".format(cmd=cmd))
            else:
                sys.stdout.write("Available tools:\n")
                for cmd in list_tools():
                    sys.stdout.write("    {cmd}\n".format(cmd=cmd))
        elif cmd == 'servers':
            config = get_current_config()
            for name, _ in config.servers.items():
                if name != DEFAULT_SERVER_SETTING:
                    sys.stdout.write("{}\n".format(name))
        else:
            sys.stderr.write("error: Unknown help command {}\n".format(cmd))
            return USER_ERROR
