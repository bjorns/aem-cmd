# coding: utf-8
import json
from StringIO import StringIO

from httmock import urlmatch, HTTMock
from mock import patch
from nose.tools import eq_, ok_

from acmd import tool_repo, Server


class MockWorkflowsService(object):
    def __init__(self):
        self.models = []
        self.instances = []

    def add_model(self, model):
        wf = {'uri': '/etc/workflow/models/{}/jcr:content/model'.format(model)}
        self.models.append(wf)

    def add_instance(self, instance):
        wf = {'uri': '/etc/workflow/instances/server0/2017-01-05/update_asset_{}'.format(instance)}
        self.instances.append(wf)


class MockHttpService(object):
    def __init__(self, task_service=None):
        self.wf_service = task_service if task_service is not None else MockWorkflowsService()
        self.request_log = []

    @urlmatch(netloc='localhost:4502')
    def __call__(self, url, request):
        self.request_log.append(request)
        if request.method == 'GET':
            if 'models' in url.path:
                return json.dumps(self.wf_service.models)
            elif 'instances' in url.path:
                return json.dumps(self.wf_service.instances)
        elif request.method == 'POST':
            return self._handle_post(url, request)

    def _handle_post(self, url, request):
        model = 'foo'
        self.wf_service.add_model(model)

        return {
            'status_code': 201,
            'content': ''
        }


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

    service = MockHttpService(task_service)

    with HTTMock(service):
        tool = tool_repo.get_tool('workflows')
        server = Server('localhost')
        status = tool.execute(server, ['workflows', 'models'])
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

    service = MockHttpService(task_service)

    with HTTMock(service):
        tool = tool_repo.get_tool('workflows')
        server = Server('localhost')
        status = tool.execute(server, ['workflows', 'instances'])
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

    service = MockHttpService(wf_service)

    with HTTMock(service):
        tool = tool_repo.get_tool('workflows')
        server = Server('localhost')
        status = tool.execute(server, ['workflows', 'start', '/dam/update_asset',
                                       '/content/dam/something/image.png/jcr:content/renditions/original'])
        eq_('', stderr.getvalue())
        ok_(stdout.getvalue().startswith('/dam/update_asset-'))
        eq_(0, status)
