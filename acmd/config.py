# coding: utf-8
import ConfigParser
from os.path import expanduser
import os.path

import acmd.server

DEFAULT_SERVER_SETTING = 'default_server'
DEFAULT_PORT = 80

def get_rcfilename():
    home = os.path.expanduser("~")
    rcfilename = "{home}/.acmd.rc".format(home=home)
    return rcfilename


class Config(object):
    def __init__(self):
        self.servers = dict()
        self.projects = dict()

    def get_server(self, server_name):
        if server_name not in self.servers:
            server_name = DEFAULT_SERVER_SETTING
        return self.servers.get(server_name)


def parse_server(parser, section):
    name = section.split(' ')[1]

    host = parser.get(section, 'host')

    port = parser.getint(section, 'port') if parser.has_option(section, 'port') else DEFAULT_PORT
    username = parser.get(section, 'username')
    password = parser.get(section, 'password')

    return acmd.server.Server(name, host=host, port=port, username=username, password=password)


def parse_servers(parser):
    ret = dict()
    for section in parser.sections():
        if section.startswith('server '):
            s = parse_server(parser, section)
            ret[s.name] = s

    default_name = parser.get('settings', DEFAULT_SERVER_SETTING)
    ret[DEFAULT_SERVER_SETTING] = ret[default_name]
    return ret


def parse_projects(parser):
    ret = {}
    if parser.has_section('projects'):
        for name, path in parser.items('projects'):
            path = expanduser(path)
            ret[name] = path
    return ret


_current_config = None
def get_current_config():
    global _current_config
    return _current_config


def read_config(filename):
    global _current_config
    parser = ConfigParser.ConfigParser()
    with open(filename) as f:
        parser.readfp(f, "utf-8")

    config = Config()
    config.servers = parse_servers(parser)
    config.projects = parse_projects(parser)
    _current_config = config
    return config
