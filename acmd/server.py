# conding: utf-8

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 4502
DEFAULT_USER = 'admin'
DEFAULT_PASS = 'admin'

class Server(object):
    def __init__(self, name, host=None, port=None, username=None, password=None):
        assert name is not None
        self.name = name
        self.host = default(host, DEFAULT_HOST)
        self.port = default(port, DEFAULT_PORT)
        self.username = default(username, DEFAULT_USER)
        self.password = default(password, DEFAULT_PASS)

    @property
    def auth(self):
        """ Default auth format for requests. """
        return self.username, self.password

    def __str__(self):
        return "http://{host}:{port}".format(host=self.host, port=self.port)

    def url(self, path):
        """ Returns a full url server from the path. """
        return "http://{host}:{port}{path}".format(
            host=self.host,
            port=self.port,
            path=path)





def default(value, defval):
    if value is None:
        return defval
    return value
