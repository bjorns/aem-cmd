# coding: utf-8
from mock import patch
from httmock import urlmatch, HTTMock
from nose.tools import eq_, ok_
from acmd import get_tool, Server, USER_ERROR, OK
from StringIO import StringIO


@urlmatch(netloc='localhost:4502', path='/libs/granite/security/post/authorizables')
def service_mock(url, request):
    with open('tests/test_data/create_group_response.html', 'rb') as f:
        data = f.read()
    return {
        'status_code': 201,
        'content': data
    }


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_print_help(stderr, stdout):
    tool = get_tool('groups')
    server = Server('localhost')
    status = tool.execute(server, ['groups'])
    eq_(USER_ERROR, status)
    ok_(len(stdout.getvalue()) > 0)
    eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_create_group(stderr, stdout):
    tool = get_tool('groups')
    server = Server('localhost')
    with HTTMock(service_mock):
        status = tool.execute(server, ['groups', 'create', 'mynewgroup1711'])
    eq_(OK, status)
    eq_('/home/groups/m/mynewgroup1711\n', stdout.getvalue())
    eq_('', stderr.getvalue())

