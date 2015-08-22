# coding: utf-8
import ConfigParser
from os.path import expanduser
import pkg_resources

import acmd.server
import acmd.tool

_DEFAULT_SERVER_SETTING = 'default_server'


def read_config_template():
    return pkg_resources.resource_string('acmd', "data/acmd.rc.template")


def setup_rcfile(rcfilename):
    """ Create a new ~/.acmd.rc from template."""
    template = read_config_template()
    target = open(rcfilename, 'wb')
    target.write(template)


class Config(object):
    def __init__(self):
        self.servers = dict()
        self.projects = dict()

    def get_server(self, server_name):
        if server_name not in self.servers:
            server_name = _DEFAULT_SERVER_SETTING
        return self.servers.get(server_name)


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


def parse_projects(parser):
    ret = {}
    if parser.has_section('projects'):
        for name, path in parser.items('projects'):
            path = expanduser(path)
            ret[name] = path
    return ret


def read_config(filename):
    parser = ConfigParser.ConfigParser()
    with open(filename) as f:
        parser.readfp(f, "utf-8")

    config = Config()
    config.servers = parse_servers(parser)
    config.projects = parse_projects(parser)
    return config
