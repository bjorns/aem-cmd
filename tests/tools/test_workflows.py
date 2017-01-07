# coding: utf-8
import json
from StringIO import StringIO

from httmock import urlmatch, HTTMock
from mock import patch
from nose.tools import eq_, ok_

from acmd import tool_repo, Server


class MockWorkflowsService(object):
    def __init__(self):
        self.workflows = []

    def list_tasks(self):
        return self.workflows

    def add_workflow(self, model):
        wf = {'uri': '/etc/workflow/models/{}/jcr:content/model'.format(model)}
        self.workflows.append(wf)


class MockHttpService(object):
    def __init__(self, task_service=None):
        self.wf_service = task_service if task_service is not None else MockWorkflowsService()
        self.request_log = []

    @urlmatch(netloc='localhost:4502')
    def __call__(self, url, request):
        self.request_log.append(request)
        if request.method == 'GET':
            return json.dumps(self.wf_service.list_tasks())
        elif request.method == 'POST':
            return self._handle_post(url, request)

    def _handle_post(self, url, request):
        model = 'foo'
        self.wf_service.add_workflow(model)

        return {
            'status_code': 201,
            'content': ''
        }


def tabbed(lines):
    lines = ['\t'.join(l) for l in lines]
    return '\n'.join(lines) + '\n'


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_list_workflows(stderr, stdout):
    task_service = MockWorkflowsService()
    task_service.add_workflow('dam/update_asset')
    task_service.add_workflow('dam/update_asset')
    task_service.add_workflow('something_else')

    service = MockHttpService(task_service)

    with HTTMock(service):
        tool = tool_repo.get_tool('workflows')
        server = Server('localhost')
        status = tool.execute(server, ['workflows', 'ls'])
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
def test_start_workflow(stderr, stdout):
    wf_service = MockWorkflowsService()

    service = MockHttpService(wf_service)

    with HTTMock(service):
        tool = tool_repo.get_tool('workflows')
        server = Server('localhost')
        status = tool.execute(server, ['workflows', 'start', '/dam/update_asset',
                                       '/content/dam/something/image.png/jcr:content/renditions/original'])
        eq_('', stderr.getvalue())
        ok_(stdout.getvalue().startswith('/dam/update_asset-'))
        eq_(0, status)
