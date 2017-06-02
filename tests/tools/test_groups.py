# coding: utf-8
from mock import patch
from httmock import urlmatch, HTTMock
from nose.tools import eq_, ok_
from acmd import tool_repo, Server, OK

from test_utils.compat import StringIO
from test_utils.console import unordered_list


@urlmatch(netloc='localhost:4502', path='/libs/granite/security/post/authorizables')
def service_mock(*_):
    with open('tests/test_data/create_group_response.html', 'rb') as f:
        data = f.read()
    return {
        'status_code': 201,
        'content': data
    }


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_print_help(stderr, stdout):
    tool = tool_repo.get_tool('group')
    server = Server('localhost')
    try:
        status = tool.execute(server, ['group', '--help'])
    except SystemExit as e:
        status = e.code
    eq_(0, status)
    ok_(len(stdout.getvalue()) > 0)
    eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_create_group(stderr, stdout):
    tool = tool_repo.get_tool('group')
    server = Server('localhost')
    with HTTMock(service_mock):
        status = tool.execute(server, ['group', 'create', 'mynewgroup1711'])
    eq_(OK, status)
    eq_('/home/groups/m/mynewgroup1711\n', stdout.getvalue())
    eq_('', stderr.getvalue())


@urlmatch(netloc='localhost:4502', path=r'/home/groups/.+')
def adduser_mock(_, request):
    eq_('addMembers=jdoe', request.body)
    with open('tests/test_data/create_group_response.html', 'rb') as f:
        data = f.read()
    return {
        'status_code': 200,
        'content': data
    }


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_add_user(stderr, stdout):
    tool = tool_repo.get_tool('group')
    server = Server('localhost')
    with HTTMock(adduser_mock):
        status = tool.execute(server, ['group', 'adduser', 'mynewgroup1711', 'jdoe'])
    eq_(OK, status)
    eq_('/home/groups/m/mynewgroup1711\n', stdout.getvalue())
    eq_('', stderr.getvalue())


@urlmatch(netloc='localhost:4502')
def list_groups_mock(*_):
    with open('tests/test_data/list_groups_response.json', 'rb') as f:
        data = f.read()
    return {
        'status_code': 200,
        'content': data
    }


EXPECTED_GROUPS = {
    "Available groups:",
    "    administrators",
    "    everyone",
    "    dam-users",
    "    mynewgroup",
    "    contributor",
    "    content-authors",
    "    mac-users",
    "    user-administrators",
    "    workflow-users",
    "    workflow-editors",
    "    tag-administrators"
}


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_groups_users(stderr, stdout):
    tool = tool_repo.get_tool('group')
    server = Server('localhost')
    with HTTMock(list_groups_mock):
        status = tool.execute(server, ['group', 'list'])
    eq_(OK, status)
    eq_(EXPECTED_GROUPS, unordered_list(stdout.getvalue()))
    eq_('', stderr.getvalue())


COMPACT_GROUPS = {
    "administrators",
    "everyone",
    "dam-users",
    "mynewgroup",
    "contributor",
    "content-authors",
    "mac-users",
    "user-administrators",
    "workflow-users",
    "workflow-editors",
    "tag-administrators"
}


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_groups_users_compact(stderr, stdout):
    tool = tool_repo.get_tool('group')
    server = Server('localhost')
    with HTTMock(list_groups_mock):
        status = tool.execute(server, ['group', 'list', '--compact'])
    eq_(OK, status)
    eq_(COMPACT_GROUPS, unordered_list(stdout.getvalue()))
    eq_('', stderr.getvalue())
