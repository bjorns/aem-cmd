# coding: utf-8
from httmock import HTTMock
from mock import patch
from nose.tools import eq_, ok_

from acmd import tool_repo, Server

from test_utils.mocks.workflow import  MockWorkflowHttpService, MockWorkflowsService
from test_utils.compat import StringIO


def tabbed(lines):
    lines = ['\t'.join(l) for l in lines]
    return '\n'.join(lines) + '\n'


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_list_models(stderr, stdout):
    task_service = MockWorkflowsService()
    task_service.add_model('dam/update_asset')
    task_service.add_model('dam/update_asset')
    task_service.add_model('something_else')

    service = MockWorkflowHttpService(task_service)

    with HTTMock(service):
        tool = tool_repo.get_tool('workflow')
        server = Server('localhost')
        status = tool.execute(server, ['workflow', 'models'])
        lines = [
            ['dam/update_asset'],
            ['dam/update_asset'],
            ['something_else'],
        ]
        eq_('', stderr.getvalue())
        eq_(tabbed(lines), stdout.getvalue())
        eq_(0, status)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_list_instances(stderr, stdout):
    task_service = MockWorkflowsService()
    task_service.add_instance('907')
    task_service.add_instance('908')
    task_service.add_instance('909')

    service = MockWorkflowHttpService(task_service)

    with HTTMock(service):
        tool = tool_repo.get_tool('workflow')
        server = Server('localhost')
        status = tool.execute(server, ['workflow', 'instances'])
        lines = [
            ['/etc/workflow/instances/server0/2017-01-05/update_asset_907'],
            ['/etc/workflow/instances/server0/2017-01-05/update_asset_908'],
            ['/etc/workflow/instances/server0/2017-01-05/update_asset_909'],
        ]
        eq_('', stderr.getvalue())
        eq_(tabbed(lines), stdout.getvalue())
        eq_(0, status)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_start_workflow(stderr, stdout):
    wf_service = MockWorkflowsService()

    service = MockWorkflowHttpService(wf_service)

    with HTTMock(service):
        tool = tool_repo.get_tool('workflow')
        server = Server('localhost')
        status = tool.execute(server, ['workflow', 'start', '/dam/update_asset',
                                       '/content/dam/something/image.png/jcr:content/renditions/original'])
        eq_('', stderr.getvalue())
        ok_(stdout.getvalue().startswith('/dam/update_asset-'))
        eq_(0, status)
