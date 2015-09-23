# conding: utf-8

DEFAULT_HOST = 'http://localhost:4502'
DEFAULT_USER = 'admin'
DEFAULT_PASS = 'admin'


class Server(object):
    """ Model of server configuration in .acmd.rc """
    def __init__(self, name, host=None, username=None, password=None, dispatcher=None):
        assert name is not None
        self.name = name
        self.host = default(host, DEFAULT_HOST)
        self.username = default(username, DEFAULT_USER)
        self.password = default(password, DEFAULT_PASS)
        self.dispatcher = dispatcher

    @property
    def auth(self):
        """ Default auth format for requests. """
        return self.username, self.password

    def __str__(self):
        return self.host

    def url(self, path):
        """ Returns a full url server from the path. """
        return "{host}{path}".format(
            host=self.host,
            path=path)


def default(value, defval):
    if value is None:
        return defval
    return value
