# coding: utf-8
import sys
from acmd.commands.registry import register_command, list_commands


class HelpCommand(object):
    def __init__(self):
        self.name = 'help'

    def execute(self, server, argv):
        sys.stdout.write("Available commands:\n")
        for cmd in list_commands():
            sys.stdout.write("  {cmd}\n".format(cmd=cmd))


cmd = HelpCommand()
register_command(cmd)
