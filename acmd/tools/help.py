# coding: utf-8
import sys

from acmd.tools.registry import register_tool, list_tools


class HelpTool(object):
    def __init__(self):
        self.name = 'help'

    def execute(self, server, argv):
        sys.stdout.write("Available tools:\n")
        for cmd in list_tools():
            sys.stdout.write("  {cmd}\n".format(cmd=cmd))


helpcmd = HelpTool()
register_tool(helpcmd)
