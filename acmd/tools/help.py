# coding: utf-8
import sys

from acmd.tools.registry import register_tool, list_tools
from acmd.tool import tool

@tool('help')
class HelpTool(object):

    def execute(self, server, argv):
        sys.stdout.write("Available tools:\n")
        for cmd in list_tools():
            sys.stdout.write("  {cmd}\n".format(cmd=cmd))
