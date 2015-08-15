# encoding: utf-8
import acmd.commands

class Command(object):
    def __init__(self, name):
        self.name = name

    def execute(self, args):
        pass
