# coding: utf-8
import os
import tempfile

from mock import patch
from nose.tools import eq_

from acmd import OK, USER_ERROR
from acmd import tool_repo, Server
from test_utils.compat import StringIO

PLAINTEXT_CONFIG = """[settings]
default_server = local

[server localhost]
host = http://localhost:4502
username = admin
password = admin

"""

ENCRYPTED_CONFIG = """[settings]
default_server = local

[server localhost]
host = http://localhost:4502
username = admin
password = {MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWaJLbnPjKCb}

"""


def create_config():
    _, filepath = tempfile.mkstemp(".rc")
    with open(filepath, 'w') as f:
        f.write(PLAINTEXT_CONFIG)
    return filepath


def load_config(filepath):
    with open(filepath, 'r') as f:
        data = f.read()
    return data


def test_format_config():
    tmp_filepath = create_config()

    tool = tool_repo.get_tool('config')
    server = Server('localhost')
    ret = tool.execute(server, ['config', 'format', '-f', tmp_filepath])

    eq_(OK, ret)
    new_config = load_config(tmp_filepath)
    eq_(PLAINTEXT_CONFIG, new_config)
    os.remove(tmp_filepath)


@patch('keyring.get_password')
@patch('acmd.util.crypto.random_bytes')
def test_encrypt_password(random_bytes, getpass):
    getpass.return_value = "foobarpass"
    random_bytes.return_value = b'0123456789abcdef'
    tmp_filepath = create_config()

    tool = tool_repo.get_tool('config')
    server = Server('localhost')
    ret = tool.execute(server, ['config', 'encrypt', '-f', tmp_filepath, 'localhost'])

    eq_(OK, ret)
    new_config = load_config(tmp_filepath)
    eq_(ENCRYPTED_CONFIG, new_config)
    os.remove(tmp_filepath)


@patch('getpass.getpass')
@patch('acmd.util.crypto.random_bytes')
def test_encrypt_decrypt(random_bytes, getpass):
    getpass.return_value = "somepassword"
    random_bytes.return_value = b'fedcba0987654321'
    tmp_filepath = create_config()

    tool = tool_repo.get_tool('config')
    server = Server('localhost')
    ret = tool.execute(server, ['config', 'encrypt', '-f', tmp_filepath, 'localhost'])

    eq_(OK, ret)
    ret = tool.execute(server, ['config', 'decrypt', '-f', tmp_filepath, 'localhost'])
    eq_(OK, ret)
    data = load_config(tmp_filepath)
    eq_(PLAINTEXT_CONFIG, data)
    os.remove(tmp_filepath)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_no_server_argument(stderr, stdout):
    _, tmp_filepath = tempfile.mkstemp(".rc")
    tool = tool_repo.get_tool('config')
    server = Server('localhost')
    ret = tool.execute(server, ['config', 'encrypt', '-f', tmp_filepath])

    eq_(USER_ERROR, ret)
    eq_('', stdout.getvalue())
    eq_('error: Missing server name argument\n', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_file_does_not_exist(stderr, stdout):
    tool = tool_repo.get_tool('config')
    server = Server('localhost')
    ret = tool.execute(server, ['config', 'encrypt', '-f', 'thisisnotafile', 'localhost'])

    eq_(USER_ERROR, ret)
    eq_('error: Requested file thisisnotafile does not exist\n', stderr.getvalue())
    eq_('', stdout.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_command_does_not_exist(stderr, stdout):
    _, tmp_filepath = tempfile.mkstemp(".rc")

    tool = tool_repo.get_tool('config')
    server = Server('localhost')
    ret = tool.execute(server, ['config', 'somethingelse', '-f', tmp_filepath])

    eq_(USER_ERROR, ret)
    eq_("error: Unknown command 'somethingelse'\n", stderr.getvalue())
    eq_('', stdout.getvalue())
    os.remove(tmp_filepath)
