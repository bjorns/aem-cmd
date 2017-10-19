# conding: utf-8
import getpass

from acmd.util.crypto import decrypt, parse_prop, make_key
from acmd.config import is_encrypted

DEFAULT_HOST = 'http://localhost:4502'
DEFAULT_USER = 'admin'
DEFAULT_PASS = 'admin'


class Server(object):
    """ Model of server configuration in .acmd.rc """

    def __init__(self, name, host=None, username=None, password=None, dispatcher=None):
        assert name is not None
        self.name = name
        self.host = _default(host, DEFAULT_HOST)
        self.username = _default(username, DEFAULT_USER)
        self._password = _default(password, DEFAULT_PASS)
        self.dispatcher = dispatcher

    @property
    def auth(self):
        """ Default auth format for requests. """
        return self.username, self.password

    @property
    def password(self):
        if is_encrypted(self._password):
            passphrase = getpass.getpass("Passphrase: ")
            iv, salt, ciphertext = parse_prop(self._password)
            key = make_key(salt, passphrase)
            plaintext_password, err = decrypt(iv, key, ciphertext)
            if err is not None:
                raise Exception(err)
            self._password = plaintext_password
        return self._password

    def __str__(self):
        """ Support debug printing the object """
        return self.host

    def url(self, path):
        """ Returns a full url server from the path. """
        return "{host}{path}".format(
            host=self.host,
            path=path)


def _default(value, defval):
    if value is None:
        return defval
    return value

