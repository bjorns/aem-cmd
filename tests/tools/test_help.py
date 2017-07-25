# coding: utf-8
from mock import patch
from nose.tools import eq_, ok_

import acmd.config
from acmd import tool_repo, Server, OK

from test_utils.compat import StringIO


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_list_tools(stderr, stdout):
    tool = tool_repo.get_tool('help')
    server = Server('localhost')
    status = tool.execute(server, ['help'])

    eq_('', stderr.getvalue())
    lines = [x.strip() for x in stdout.getvalue().split('\n')]
    eq_("Available tools:", lines[0])
    ok_(len(lines) > 5)

    ok_('bundle' in lines)
    ok_('cat' in lines)
    ok_('cp' in lines)
    ok_('find' in lines)
    ok_('groovy' in lines)
    ok_('group' in lines)
    ok_('help' in lines)
    ok_('install_bash_completion' in lines)
    ok_('ls' in lines)
    ok_('mv' in lines)
    ok_('package' in lines)
    ok_('rm' in lines)
    ok_('rmprop' in lines)
    ok_('search' in lines)
    ok_('setprop' in lines)
    ok_('storage' in lines)
    ok_('user' in lines)
    ok_('workflow' in lines)
    eq_(OK, status)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_list_tools(stderr, stdout):
    tool = tool_repo.get_tool('help')
    server = Server('localhost')
    status = tool.execute(server, ['help', '--compact'])

    eq_('', stderr.getvalue())
    lines = [x for x in stdout.getvalue().split('\n')]
    ok_(len(lines) > 5)
    ok_('bundle' in lines)
    ok_('cat' in lines)
    ok_('cp' in lines)
    ok_('find' in lines)
    ok_('groovy' in lines)
    ok_('group' in lines)
    ok_('help' in lines)
    ok_('install_bash_completion' in lines)
    ok_('ls' in lines)
    ok_('mv' in lines)
    ok_('package' in lines)
    ok_('rm' in lines)
    ok_('rmprop' in lines)
    ok_('search' in lines)
    ok_('setprop' in lines)
    ok_('storage' in lines)
    ok_('user' in lines)
    ok_('workflow' in lines)
    eq_(OK, status)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_list_servers(stderr, stdout):
    config = acmd.config.Config()
    config.servers['server1'] = Server('server1')
    config.servers['server2'] = Server('server2')
    config.servers['server3'] = Server('server3')

    tool = tool_repo.get_tool('help')
    tool.config = config
    server = Server('localhost')
    status = tool.execute(server, ['help', '_servers'])

    eq_('', stderr.getvalue())
    lines = [x.strip() for x in stdout.getvalue().split('\n')]

    eq_('server1', lines[0])
    eq_('server2', lines[1])
    eq_('server3', lines[2])
    eq_(OK, status)


EXPECTED_BUNDLE_HELP_MESSAGE = """Usage: acmd bundle [options] [list|start|stop] [<bundle>]

Options:
  -h, --help     show this help message and exit
  -r, --raw      output raw response data
  -c, --compact  output only package name
"""


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_tool_help(stderr, stdout):
    config = acmd.config.Config()
    config.servers['server1'] = Server('server1')
    config.servers['server2'] = Server('server2')
    config.servers['server3'] = Server('server3')

    tool = tool_repo.get_tool('help')

    tool.config = config
    server = Server('localhost')
    status = tool.execute(server, ['help', 'bundle'])
    eq_(OK, status)
    eq_('', stderr.getvalue())
    eq_(EXPECTED_BUNDLE_HELP_MESSAGE, stdout.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_help_for_non_existing_tool(stderr, stdout):
    config = acmd.config.Config()
    config.servers['server1'] = Server('server1')
    config.servers['server2'] = Server('server2')
    config.servers['server3'] = Server('server3')

    tool = tool_repo.get_tool('help')

    tool.config = config
    server = Server('localhost')

    try:
        tool.execute(server, ['help', 'doesnt-exist'])
        assert False
    except Exception as e:
        eq_('Tool doesnt-exist is missing', str(e))


