# coding: utf-8
import sys

from acmd import tool, list_tools

@tool('tools')
class ToolsTool(object):

    def execute(self, server, argv):
        for cmd in list_tools():
            sys.stdout.write("{cmd}\n".format(cmd=cmd))
