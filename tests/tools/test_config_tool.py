# coding: utf-8
import os
import tempfile

from mock import patch
from nose.tools import eq_

from acmd import OK
from acmd import tool_repo, Server
from acmd.tools.config_tool import encrypt_str, decrypt_str

CONFIG = """[settings]
default_server = local

[server localhost]
host = http://localhost:4502
username = admin
password = admin"""

ENCRYPTED_CONFIG = """[settings]
default_server = local

[server localhost]
host = http://localhost:4502
username = admin
password = [3aTbniprRw==]
password_iv = MDEyMzQ1Njc4OWFiY2RlZg==

"""

@patch('getpass.getpass')
@patch('acmd.tools.config_tool.get_iv')
def test_encrypt_password(get_iv, getpass):
    getpass.return_value = "foobarpass"
    get_iv.return_value = b'0123456789abcdef'

    _, tmp_filepath = tempfile.mkstemp(".rc")
    with open(tmp_filepath, 'w') as f:
        f.write(CONFIG)

    tool = tool_repo.get_tool('config')
    server = Server('localhost')
    ret = tool.execute(server, ['config', 'encrypt', tmp_filepath])
    eq_(OK, ret)

    with open(tmp_filepath, 'r') as f:
        data = f.read()

    eq_(ENCRYPTED_CONFIG, data)

    os.remove(tmp_filepath)


def test_encrypt_decrypt_str():
    IV = b'This is an IV456'
    msg = "Hello Wörld"
    key = b'Some kind of key'
    data = encrypt_str(IV, key, msg)
    eq_("SapMLwk/NqcHuy4y", data)
    new_msg = decrypt_str(IV, key, data)
    eq_(msg, new_msg)
