# coding: utf-8
import json
from StringIO import StringIO
import sys
from httmock import urlmatch, HTTMock
from mock import patch
from nose.tools import eq_

from acmd import get_tool, Server
import acmd.logger


class MockTaskService(object):
    def __init__(self):
        self.tasks = dict()

    def create_task(self, task_id, path):
        self.tasks[task_id] = self._new_task(task_id, path)

    @staticmethod
    def _new_task(task_id, path):
        return {
            'id': task_id,
            'dst': path,
            "src": "http://admin:admin@localhost:4503/crx/server/-/jcr:root{}".format(path),
            'status': {
                'state': 'NEW'
            }
        }

    def start_task(self, task_id):
        self.tasks[task_id]['status']['state'] = 'RUNNING'

    def remove_task(self, task_id):
        del self.tasks[task_id]

    def list_tasks(self):
        for task_id, task in self.tasks.items():
            if task['status']['state'] == 'RUNNING':
                self.tasks[task_id]['status']['state'] = 'FINISHED'
        return {
            'tasks': self.tasks.values()
        }


task_service = None
posted_data = None


@urlmatch(netloc='localhost:4502')
def mock_http_task_service(url, request):
    global task_service

    if request.method == 'GET':
        eq_('/system/jackrabbit/filevault/rcp', url.path)
        return json.dumps(task_service.list_tasks())
    elif request.method == 'POST':
        return _handle_post(url, request)


def _handle_post(url, request):
    global posted_data
    global task_service

    eq_('/system/jackrabbit/filevault/rcp', url.path)
    posted_data = json.loads(request.body)

    if posted_data['cmd'] == 'create':
        task_id = posted_data['id']
        task_service.create_task(task_id, posted_data['dst'])

        return {
            'status_code': 201,
            'content': json.dumps({"status": "ok", "id": task_id})
        }
    elif posted_data['cmd'] == 'start':
        task_id = posted_data['id']
        task_service.start_task(task_id)
        body = json.dumps({
            "status": "ok",
            "id": task_id
        })
        return body
    elif posted_data['cmd'] == 'remove':
        task_id = posted_data['id']
        task_service.remove_task(task_id)
        return json.dumps({
            "status": "ok",
            "id": task_id
        })
    else:
        raise Exception("Unknown command " + posted_data['cmd'])


def tabbed(lines):
    lines = ['\t'.join(l) for l in lines]
    return '\n'.join(lines) + '\n'


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rcp_ls(stderr, stdout):
    global task_service
    task_service = MockTaskService()
    task_service.create_task('task_id_4711', '/content/dam/something')
    task_service.create_task('task_id_4712', '/content/dam/something_else')
    task_service.start_task('task_id_4711')

    with HTTMock(mock_http_task_service):
        tool = get_tool('rcp')
        server = Server('localhost')
        status = tool.execute(server, ['ls'])
        eq_(0, status)
        lines = [
            ['task_id_4711', 'localhost:4503', '/content/dam/something', 'FINISHED'],
            ['task_id_4712', 'localhost:4503', '/content/dam/something_else', 'NEW']
        ]
        eq_(tabbed(lines), stdout.getvalue())
        eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rcp_create(stderr, stdout):
    global posted_data
    global task_service
    task_service = MockTaskService()

    with HTTMock(mock_http_task_service):
        tool = get_tool('rcp')
        server = Server('localhost')
        status = tool.execute(server,
                              ['rcp', 'create', '-s', 'other-host:4502', '-c', 'user:pass', '/content/dam/data'])

        eq_('http://user:pass@other-host:4502/crx/-/jcr:root/content/dam/data', posted_data['src'])

        eq_(0, status)
        eq_('{}\n'.format(posted_data['id']), stdout.getvalue())
        eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rcp_start(stderr, stdout):
    global task_service
    task_service = MockTaskService()
    task_service.create_task('rcp-0ed9f8', '/content/dam/something')

    with HTTMock(mock_http_task_service):
        tool = get_tool('rcp')
        server = Server('localhost')
        status = tool.execute(server, ['rcp', 'start', 'rcp-0ed9f8'])
        eq_(0, status)
        eq_('', stdout.getvalue())
        eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rcp_rm(stderr, stdout):
    global task_service
    task_service = MockTaskService()
    task_service.create_task('rcp-0ed9f8', 'rcp-0ed9f8')

    with HTTMock(mock_http_task_service):
        tool = get_tool('rcp')
        server = Server('localhost')
        status = tool.execute(server, ['rcp', 'rm', 'rcp-0ed9f8'])
        eq_(0, status)
        eq_('', stdout.getvalue())
        eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rcp_fetch(stderr, stdout):
    global task_service
    task_service = MockTaskService()

    with HTTMock(mock_http_task_service):
        tool = get_tool('rcp')
        server = Server('localhost')
        status = tool.execute(server, ['rcp', 'fetch', '-s', 'other-server:4502', '-c',
                                       '"jdoe:abc123"', '/content/dam/test-fetch'])
        eq_('', stdout.getvalue())
        eq_('', stderr.getvalue())
        eq_(0, status)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rcp_clear(stderr, stdout):
    global task_service
    task_service = MockTaskService()
    task_service.create_task('task_id_4711', '/content/dam/something')
    task_service.create_task('task_id_4712', '/content/dam/something_else')
    task_service.start_task('task_id_4711')

    eq_(2, len(task_service.tasks))

    with HTTMock(mock_http_task_service):
        tool = get_tool('rcp')
        server = Server('localhost')
        status = tool.execute(server, ['rcp', 'clear'])
        eq_(0, status)
        eq_(0, len(task_service.tasks))
        eq_('', stderr.getvalue())
        eq_('', stdout.getvalue())
