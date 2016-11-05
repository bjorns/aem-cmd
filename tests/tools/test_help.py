# coding: utf-8
from StringIO import StringIO

from mock import patch
from nose.tools import eq_, ok_

from acmd import get_tool, Server, OK
import acmd.config


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_list_tools(stderr, stdout):
    tool = get_tool('help')
    server = Server('localhost')
    status = tool.execute(server, ['help'])

    lines = [x.strip() for x in stdout.getvalue().split('\n')]
    eq_("Available tools:", lines[0])
    ok_(len(lines) > 5)

    ok_('bundles' in lines)
    ok_('cat' in lines)
    ok_('cp' in lines)
    ok_('dispatcher' in lines)
    ok_('find' in lines)
    ok_('groovy' in lines)
    ok_('groups' in lines)
    ok_('help' in lines)
    ok_('install_bash_completion' in lines)
    ok_('jobs' in lines)
    ok_('ls' in lines)
    ok_('mv' in lines)
    ok_('packages' in lines)
    ok_('rcp' in lines)
    ok_('rm' in lines)
    ok_('rmprop' in lines)
    ok_('search' in lines)
    ok_('setprop' in lines)
    ok_('storage' in lines)
    ok_('users' in lines)
    ok_('workflows' in lines)
    eq_(OK, status)

@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_list_tools(stderr, stdout):
    tool = get_tool('help')
    server = Server('localhost')
    status = tool.execute(server, ['help', '--compact'])

    lines = [x for x in stdout.getvalue().split('\n')]
    ok_(len(lines) > 5)
    ok_('bundles' in lines)
    ok_('cat' in lines)
    ok_('cp' in lines)
    ok_('dispatcher' in lines)
    ok_('find' in lines)
    ok_('groovy' in lines)
    ok_('groups' in lines)
    ok_('help' in lines)
    ok_('install_bash_completion' in lines)
    ok_('jobs' in lines)
    ok_('ls' in lines)
    ok_('mv' in lines)
    ok_('packages' in lines)
    ok_('rcp' in lines)
    ok_('rm' in lines)
    ok_('rmprop' in lines)
    ok_('search' in lines)
    ok_('setprop' in lines)
    ok_('storage' in lines)
    ok_('users' in lines)
    ok_('workflows' in lines)
    eq_(OK, status)

@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_list_servers(stderr, stdout):

    config = acmd.config.Config()
    config.servers['server1'] = Server('server1')
    config.servers['server2'] = Server('server2')
    config.servers['server3'] = Server('server3')
    acmd.config._current_config = config

    tool = get_tool('help')
    server = Server('localhost')
    status = tool.execute(server, ['help', '_servers'])
    lines = [x.strip() for x in stdout.getvalue().split('\n')]

    eq_('server1', lines[0])
    eq_('server2', lines[1])
    eq_('server3', lines[2])
    eq_(OK, status)
