import acmd.command

class Inspect(object):
    def __init__(self):
        self.name = 'inspect'

    def execute(self, args):
        print("Inspecting!")
