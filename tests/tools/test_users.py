# coding: utf-8
from mock import patch
from httmock import urlmatch, HTTMock
from nose.tools import eq_, ok_

from acmd import tool_repo, Server, OK

from test_utils.http import parse_body
from test_utils.compat import StringIO
from test_utils.console import unordered_list


@urlmatch(netloc='localhost:4502', path='/libs/granite/security/post/authorizables')
def create_service_mock(*_):
    with open('tests/test_data/create_user_response.html', 'rb') as f:
        data = f.read()
    return {
        'status_code': 201,
        'content': data
    }


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_print_help(stderr, stdout):
    tool = tool_repo.get_tool('user')
    server = Server('localhost')
    try:
        status = tool.execute(server, ['user', '--help'])
    except SystemExit as e:
        status = e.code
    eq_(0, status)
    ok_(len(stdout.getvalue()) > 0)
    eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_create_user(stderr, stdout):
    tool = tool_repo.get_tool('user')
    server = Server('localhost')
    with HTTMock(create_service_mock):
        status = tool.execute(server, ['user', 'create', '--password=passwd', 'jdoe'])
    eq_(OK, status)
    eq_('/home/users/j/jdoe\n', stdout.getvalue())
    eq_('', stderr.getvalue())


@urlmatch(netloc='localhost:4502', path='/home/users/j/jdoe.rw.html')
def setprop_service_mock(_, request):
    with open('tests/test_data/create_user_response.html') as f:
        data = f.read()

    expected = {'profile/prop0': 'val0', 'profile/prop1@TypeHint': 'String', 'profile/prop1': 'Quoted+value'}
    eq_(expected, parse_body(request.body))
    return {
        'status_code': 200,
        'content': data
    }


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_set_property(stderr, stdout):
    tool = tool_repo.get_tool('user')
    server = Server('localhost')
    with HTTMock(setprop_service_mock):
        status = tool.execute(server, ['user', 'setprop', 'jdoe', 'prop0=val0,prop1="Quoted value"'])
    eq_(OK, status)
    eq_('/home/users/j/jdoe\n', stdout.getvalue())
    eq_('', stderr.getvalue())


@urlmatch(netloc='localhost:4502')
def list_users_mock(*_):
    with open('tests/test_data/list_users_response.json', 'rb') as f:
        data = f.read()
    return {
        'status_code': 200,
        'content': data
    }


EXPECTED_RESPONSE = {
    "Available users:",
    "    admin",
    "    anonymous",
    "    jdoe",
    "    rep:policy",
    "    replication-receiver",
    "    previewer"
}


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_list_users(stderr, stdout):
    tool = tool_repo.get_tool('user')
    server = Server('localhost')
    with HTTMock(list_users_mock):
        status = tool.execute(server, ['user', 'list'])
    eq_(OK, status)
    eq_(EXPECTED_RESPONSE, unordered_list(stdout.getvalue()))
    eq_('', stderr.getvalue())


COMPACT_RESPONSE = {
    "admin",
    "anonymous",
    "jdoe",
    "rep:policy",
    "replication-receiver",
    "previewer"
}


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_list_users_compact(stderr, stdout):
    tool = tool_repo.get_tool('user')
    server = Server('localhost')
    with HTTMock(list_users_mock):
        status = tool.execute(server, ['user', 'list', '--compact'])
    eq_(OK, status)
    eq_(COMPACT_RESPONSE, unordered_list(stdout.getvalue()))
    eq_('', stderr.getvalue())
