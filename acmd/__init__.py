# coding: utf-8
import acmd.command
import acmd.server

Command = command.Command
registry = {
    'inspect': commands.Inspect()
}

def get_command(cmd_name):
    return registry[cmd_name]

get_server = server.get_server
