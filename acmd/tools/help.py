# coding: utf-8
import sys

from acmd.tool import tool, list_tools

@tool('help')
class HelpTool(object):

    def execute(self, server, argv):
        sys.stdout.write("Available tools:\n")
        for cmd in list_tools():
            sys.stdout.write("  {cmd}\n".format(cmd=cmd))
