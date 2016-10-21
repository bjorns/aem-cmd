# coding: utf-8
import json
from StringIO import StringIO
from mock import patch

from httmock import urlmatch
from nose.tools import eq_
from httmock import urlmatch, HTTMock

from acmd import get_tool, Server


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
        self.task_service = task_service if task_service is not None else MockWorkflowsService()
        self.request_log = []

    @urlmatch(netloc='localhost:4502')
    def __call__(self, url, request):
        self.request_log.append(request)

        if request.method == 'GET':
            return json.dumps(self.task_service.list_tasks())
        elif request.method == 'POST':
            return self._handle_post(url, request)

    def _handle_post(self, url, request):
        pass


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
        tool = get_tool('workflows')
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


def test_start_workflow():
    pass
