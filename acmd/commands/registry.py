# coding: utf-8

_commands = dict()

def register_command(cmd):
    assert get_command(cmd.name) is None
    _commands[cmd.name] = cmd


def get_command(cmd_name):
    return _commands.get(cmd_name)

def list_commands():
    """ Returns list of all command names."""
    return _commands.keys()
