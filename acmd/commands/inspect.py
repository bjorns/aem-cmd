# coding: utf-8
import acmd.command
from acmd.commands.registry import register_command

class Inspect(object):
    def __init__(self):
        self.name = 'inspect'

    def execute(self, args):
        print("Inspecting!")


cmd = Inspect()
register_command(cmd)
