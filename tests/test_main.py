# coding: utf-8
from StringIO import StringIO

from nose.tools import eq_

from mock import patch

from acmd import tool, get_tool, __version__
from acmd.main import main


@tool('mock_tool')
class MockTool(object):
    def __init__(self):
        self.did_run = False

    def execute(self, server, argv):
        self.did_run = True
        return 1147


@patch('sys.stdout', new_callable=StringIO)
def test_show_version(stdout):
    args = ['acmd', '--version']

    try:
        main(args)
    except SystemExit as e:
        pass

    eq_(__version__ + '\n', stdout.getvalue())


@patch('acmd.main.load_projects')
def test_run_tool(load_proj):
    _tool = get_tool('mock_tool')
    eq_(False, _tool.did_run)

    args = ['acmd', 'mock_tool']
    try:
        exit_code = 0
        main(args)
    except SystemExit as e:
        exit_code = e.code
    eq_(1147, exit_code)

    eq_(True, load_proj.called)
    _tool = get_tool('mock_tool')
    eq_(True, _tool.did_run)
