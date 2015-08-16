# conding: utf-8
import configparser

DEFAULT_SERVER_SETTING = 'default_server'

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 4502
DEFAULT_USER = 'admin'
DEFAULT_PASS = 'admin'

class Server(object):
    def __init__(self, name, host='localhost', port=4502, username='admin', password='admin'):
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def __str__(self):
        return "http://{host}:{port}".format(host=self.host,port=self.port)

    def url(self, path):
        return "http://{host}:{port}{path}".format(
            host=self.host,
            port=self.port,
            path=path)


def get_server(server_name):
    if server_name is None:
        server_name = DEFAULT_SERVER_SETTING
    cfg = read_config("/Users/bjorn/.aem-cmd")
    return cfg[server_name]


def read_config(filename):
    parser = configparser.ConfigParser()
    with open(filename) as f:
        parser.read_file(f, "utf-8")

    ret = dict()
    for section in parser.sections():
        if section.startswith('server '):
            name = section.split(' ')[1]
            s = Server(name)
            s.host = default(parser.get(section, 'host'), DEFAULT_HOST)
            s.port = default(parser.get(section, 'port'), DEFAULT_PORT)
            s.username = default(parser.get(section, 'username'), DEFAULT_USER)
            s.password = default(parser.get(section, 'password'), DEFAULT_PASS)
            ret[name] = s

    default_name = parser.get('settings', DEFAULT_SERVER_SETTING)
    ret[DEFAULT_SERVER_SETTING] = ret[default_name]
    return ret

def default(value, default):
    if value is None:
        return default
    return value
