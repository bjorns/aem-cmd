# coding: utf-8
from acmd import get_tool, Server, OK
from StringIO import StringIO

from mock import patch
from httmock import urlmatch, HTTMock
from nose.tools import eq_, ok_


@urlmatch(netloc='localhost:4502', path='/libs/granite/security/post/authorizables')
def create_service_mock(url, request):
    with open('tests/test_data/create_user_response.html', 'rb') as f:
        data = f.read()
    return {
        'status_code': 201,
        'content': data
    }


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_print_help(stderr, stdout):
    tool = get_tool('users')
    server = Server('localhost')
    try:
        tool.execute(server, ['users', '--help'])
    except SystemExit as e:
        status = e.code
    eq_(0, status)
    ok_(len(stdout.getvalue()) > 0)
    eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_create_user(stderr, stdout):
    tool = get_tool('users')
    server = Server('localhost')
    with HTTMock(create_service_mock):
        status = tool.execute(server, ['users', 'create', '--password=passwd', 'jdoe'])
    eq_(OK, status)
    eq_('/home/users/j/jdoe\n', stdout.getvalue())
    eq_('', stderr.getvalue())


@urlmatch(netloc='localhost:4502', path='/home/users/j/jdoe.rw.html')
def setprop_service_mock(url, request):
    with open('tests/test_data/create_user_response.html', 'rb') as f:
        data = f.read()
    eq_('profile%2Fprop0=val0&profile%2Fprop1=Quoted+value&profile%2Fprop1%40TypeHint=String', request.body)
    return {
        'status_code': 200,
        'content': data
    }


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_set_property(stderr, stdout):
    tool = get_tool('users')
    server = Server('localhost')
    with HTTMock(setprop_service_mock):
        status = tool.execute(server, ['users', 'setprop', 'jdoe', 'prop0=val0,prop1="Quoted value"'])
    eq_(OK, status)
    eq_('/home/users/j/jdoe\n', stdout.getvalue())
    eq_('', stderr.getvalue())


@urlmatch(netloc='localhost:4502')
def list_users_mock(url, request):
    with open('tests/test_data/list_users_response.json', 'rb') as f:
        data = f.read()
    return {
        'status_code': 200,
        'content': data
    }


EXPECTED_RESPONSE = """Available users:
    admin
    anonymous
    jdoe
    rep:policy
    replication-receiver
    previewer
"""


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_list_users(stderr, stdout):
    tool = get_tool('users')
    server = Server('localhost')
    with HTTMock(list_users_mock):
        status = tool.execute(server, ['users', 'list'])
    eq_(OK, status)
    eq_(EXPECTED_RESPONSE, stdout.getvalue())
    eq_('', stderr.getvalue())


COMPACT_RESPONSE = """admin
anonymous
jdoe
rep:policy
replication-receiver
previewer
"""


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_list_users_compact(stderr, stdout):
    tool = get_tool('users')
    server = Server('localhost')
    with HTTMock(list_users_mock):
        status = tool.execute(server, ['users', 'list', '--compact'])
    eq_(OK, status)
    eq_(COMPACT_RESPONSE, stdout.getvalue())
    eq_('', stderr.getvalue())
