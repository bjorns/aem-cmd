# coding: utf-8
""" Support for reading .acmd.rc config files. """

from configparser import ConfigParser

import os.path

import acmd.server

DEFAULT_SERVER_SETTING = 'default_server'


def get_rcfilename():
    """ Returns the full path of the acmd config file. """
    home = os.path.expanduser("~")
    rcfilename = "{home}/.acmd.rc".format(home=home)
    return rcfilename


class Config(object):
    """ Model of the current config file. """

    def __init__(self):
        self.servers = dict()
        self.projects = dict()

    def get_server(self, server_name):
        if server_name is None:
            server_name = DEFAULT_SERVER_SETTING
        return self.servers.get(server_name, None)


def parse_server(parser, section):
    """ Parse a [server] entry in the config file. Returns a server.Server object. """
    name = section.split(' ')[1]

    host = parser.get(section, 'host')

    username = parser.get(section, 'username')
    password = parser.get(section, 'password')
    if parser.has_option(section, 'dispatcher'):
        dispatcher = parser.get(section, 'dispatcher')
    else:
        dispatcher = None

    return acmd.server.Server(name,
                              host=host,
                              username=username,
                              password=password,
                              dispatcher=dispatcher)


def parse_servers(parser):
    """ Parse all [server] entries in the config file.
        Returns a dictionary mapping the server names to Server() instances.
     """
    ret = dict()
    for section in parser.sections():
        if section.startswith('server '):
            server = parse_server(parser, section)
            ret[server.name] = server

    default_name = parser.get('settings', DEFAULT_SERVER_SETTING)
    ret[DEFAULT_SERVER_SETTING] = ret[default_name]
    return ret


def parse_projects(parser):
    """ Parse all entries under the [projects] section in the config file.
        Returns a dictionary from the name to the full expanded path of the
        project dir.
    """
    ret = dict()
    if parser.has_section('projects'):
        for name, path in parser.items('projects'):
            path = os.path.expanduser(path)
            ret[name] = path
    return ret


def read_config(filename):
    """ Read the config file filename. Return a Config() object. """
    parser = ConfigParser()
    with open(filename) as f:
        parser.readfp(f, "utf-8")

    config = Config()
    config.servers = parse_servers(parser)
    config.projects = parse_projects(parser)
    return config


def is_encrypted(password):
    """ Returns true if password string is encrypted. """
    return password.startswith('{') and password.endswith('}')
