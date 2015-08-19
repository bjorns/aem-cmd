# coding: utf-8
import ConfigParser
import acmd.server

_DEFAULT_SERVER_SETTING = 'default_server'


class Config(object):
    def __init__(self):
        self.servers = dict()
        self.projects = list()

    def get_server(self, server_name):
        if server_name is None:
            server_name = _DEFAULT_SERVER_SETTING

        return self.servers[server_name]


def parse_server(parser, section):
    name = section.split(' ')[1]

    host = parser.get(section, 'host')
    port = parser.get(section, 'port')
    username = parser.get(section, 'username')
    password = parser.get(section, 'password')

    return acmd.server.Server(name, host=host, port=port, username=username, password=password)


def parse_servers(parser):
    ret = dict()
    for section in parser.sections():
        if section.startswith('server '):
            s = parse_server(parser, section)
            ret[s.name] = s

    default_name = parser.get('settings', _DEFAULT_SERVER_SETTING)
    ret[_DEFAULT_SERVER_SETTING] = ret[default_name]
    return ret


def read_config(filename):
    parser = ConfigParser.ConfigParser()
    with open(filename) as f:
        parser.readfp(f, "utf-8")

    config = Config()
    config.servers = parse_servers(parser)
    return config

