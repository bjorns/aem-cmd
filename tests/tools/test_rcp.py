# coding: utf-8
import json
from StringIO import StringIO
from httmock import urlmatch, HTTMock
from mock import patch
from nose.tools import eq_

from acmd import get_tool, Server


class MockTaskService(object):
    def __init__(self):
        self.tasks = dict()
        self.log = []

    @staticmethod
    def _new_task(task_id, src_path, dst_path):
        return {
            'id': task_id,
            "src": "http://admin:admin@localhost:4503/crx/server/-/jcr:root{}".format(src_path),
            'dst': dst_path,
            'status': {
                'state': 'NEW'
            }
        }

    def create_task(self, task_id, src_path, dst_path=None):
        if dst_path is None:
            dst_path = src_path
        self.log.append('create')
        self.tasks[task_id] = self._new_task(task_id, src_path, dst_path)

    def start_task(self, task_id):
        self.log.append('start')
        self.tasks[task_id]['status']['state'] = 'RUNNING'

    def stop_task(self, task_id):
        self.log.append('stop')
        self.tasks[task_id]['status']['state'] = 'STOPPED'

    def remove_task(self, task_id):
        self.log.append('remove')
        del self.tasks[task_id]

    def list_tasks(self):
        self.log.append('list')
        for task_id, task in self.tasks.items():
            if task['status']['state'] == 'RUNNING':
                self.tasks[task_id]['status']['state'] = 'FINISHED'
        return {
            'tasks': self.tasks.values()
        }


class MockHttpService(object):

    def __init__(self, task_service=None):
        self.task_service = task_service if task_service is not None else MockTaskService()
        self.request_log = []

    @urlmatch(netloc='localhost:4502')
    def __call__(self, url, request):
        self.request_log.append(request)

        if request.method == 'GET':
            eq_('/system/jackrabbit/filevault/rcp', url.path)
            return json.dumps(self.task_service.list_tasks())
        elif request.method == 'POST':
            return self._handle_post(url, request)

    def _handle_post(self, url, request):

        eq_('/system/jackrabbit/filevault/rcp', url.path)
        data = json.loads(request.body)

        if data['cmd'] == 'create':
            task_id = data['id']
            self.task_service.create_task(task_id, data['src'], data['dst'])

            return {
                'status_code': 201,
                'content': json.dumps({"status": "ok", "id": task_id})
            }
        elif data['cmd'] == 'start':
            task_id = data['id']
            self.task_service.start_task(task_id)
            body = json.dumps({
                "status": "ok",
                "id": task_id
            })
            return body
        elif data['cmd'] == 'stop':
            task_id = data['id']
            self.task_service.stop_task(task_id)
            body = json.dumps({
                "status": "ok",
                "id": task_id
            })
            return body
        elif data['cmd'] == 'remove':
            task_id = data['id']
            self.task_service.remove_task(task_id)
            return json.dumps({
                "status": "ok",
                "id": task_id
            })
        else:
            raise Exception("Unknown command " + data['cmd'])


def tabbed(lines):
    lines = ['\t'.join(l) for l in lines]
    return '\n'.join(lines) + '\n'


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rcp_ls(stderr, stdout):
    task_service = MockTaskService()
    task_service.create_task('task_id_4711', '/content/dam/something')
    task_service.create_task('task_id_4712', '/content/dam/something_else', '/content/dam/new target')
    task_service.start_task('task_id_4711')

    service = MockHttpService(task_service)

    with HTTMock(service):
        tool = get_tool('rcp')
        server = Server('localhost')
        status = tool.execute(server, ['ls'])
        eq_(0, status)
        lines = [
            ['task_id_4711', 'localhost:4503/content/dam/something', '/content/dam/something', 'FINISHED'],
            ['task_id_4712', 'localhost:4503/content/dam/something_else', '/content/dam/new target', 'NEW']
        ]
        eq_(tabbed(lines), stdout.getvalue())
        eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rcp_create(stderr, stdout):

    service = MockHttpService()

    with HTTMock(service):
        tool = get_tool('rcp')
        server = Server('localhost')
        status = tool.execute(server,
                              ['rcp', 'create', '-s', 'other-host:4502', '-c', 'user:pass', '/content/dam/data'])

        eq_(1, len(service.request_log))
        data = json.loads(service.request_log[0].body)
        eq_('http://user:pass@other-host:4502/crx/-/jcr:root/content/dam/data', data['src'])

        eq_(0, status)
        eq_('{}\n'.format(data['id']), stdout.getvalue())
        eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rcp_start(stderr, stdout):
    task_service = MockTaskService()
    task_service.create_task('rcp-0ed9f8', '/content/dam/something')
    service = MockHttpService(task_service)

    with HTTMock(service):
        tool = get_tool('rcp')
        server = Server('localhost')
        # TODO: Run tests without force flag
        status = tool.execute(server, ['rcp', 'start', 'rcp-0ed9f8', '--force'])
        eq_(0, status)
        eq_('', stdout.getvalue())
        eq_('', stderr.getvalue())

    eq_('RUNNING', task_service.tasks['rcp-0ed9f8']['status']['state'])


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rcp_stop(stderr, stdout):
    task_service = MockTaskService()
    task_service.create_task('rcp-0ed9f8', '/content/dam/something')
    task_service.start_task('rcp-0ed9f8')
    service = MockHttpService(task_service)

    with HTTMock(service):
        tool = get_tool('rcp')
        server = Server('localhost')
        # TODO: Run tests without force flag
        status = tool.execute(server, ['rcp', 'stop', 'rcp-0ed9f8', '--force'])
        eq_(0, status)
        eq_('', stdout.getvalue())
        eq_('', stderr.getvalue())

    eq_('STOPPED', task_service.tasks['rcp-0ed9f8']['status']['state'])


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rcp_rm(stderr, stdout):
    task_service = MockTaskService()
    task_service.create_task('rcp-0ed9f8', 'rcp-0ed9f8')
    service = MockHttpService(task_service)

    with HTTMock(service):
        tool = get_tool('rcp')
        server = Server('localhost')
        status = tool.execute(server, ['rcp', 'rm', 'rcp-0ed9f8'])
        eq_(0, status)
        eq_('', stdout.getvalue())
        eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rcp_fetch(stderr, stdout):
    service = MockHttpService()

    with HTTMock(service):
        tool = get_tool('rcp')
        server = Server('localhost')
        # TODO: Run tests without force flag
        status = tool.execute(server, ['rcp', 'fetch', '-s', 'other-server:4502', '-c',
                                       '"jdoe:abc123"', '/content/dam/test-fetch', '--force'])
        eq_('', stdout.getvalue())
        eq_('', stderr.getvalue())
        eq_(0, status)

    eq_(['create', 'list', 'start', 'list', 'remove'], service.task_service.log)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rcp_clear(stderr, stdout):

    task_service = MockTaskService()
    task_service.create_task('task_id_4711', '/content/dam/something')
    task_service.create_task('task_id_4712', '/content/dam/something_else')
    task_service.start_task('task_id_4711')

    service = MockHttpService(task_service)

    eq_(2, len(task_service.tasks))

    with HTTMock(service):
        tool = get_tool('rcp')
        server = Server('localhost')
        status = tool.execute(server, ['rcp', 'clear'])
        eq_(0, status)
        eq_(0, len(task_service.tasks))
        eq_('', stderr.getvalue())
        eq_('', stdout.getvalue())

    eq_(3, len(service.request_log))
    eq_(['create', 'create', 'start', 'list', 'remove', 'remove'], task_service.log)
