# coding: utf-8
from nose.tools import eq_

from mock import patch

from acmd import tool, tool_repo, __version__
from acmd.main import main

from test_utils.compat import StringIO


@tool('mock_tool')
class MockTool(object):
    def __init__(self):
        self.did_run = False

    def execute(self, *_):
        self.did_run = True
        return 1147


@patch('sys.stdout', new_callable=StringIO)
def test_show_version(stdout):
    args = ['acmd', '--version']
    try:
        tool_repo.reset()
        main(args, rcfile="tests/test_data/test_acmd.rc")
    except SystemExit:
        pass

    eq_(__version__ + '\n', stdout.getvalue())


@patch('acmd.import_projects')
@patch('acmd.deploy.deploy_bash_completion')
def test_run_tool(_, load_proj):
    _tool = tool_repo.get_tool('mock_tool')
    eq_(False, _tool.did_run)

    args = ['acmd', 'mock_tool']
    try:
        exit_code = 0
        main(args)
    except SystemExit as e:
        exit_code = e.code
    eq_(1147, exit_code)

    eq_(True, load_proj.called)
    
    _tool = tool_repo.get_tool('mock_tool')
    eq_(True, _tool.did_run)
