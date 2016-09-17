# coding: utf-8
import json
from StringIO import StringIO

from httmock import urlmatch, HTTMock
from mock import patch
from nose.tools import eq_

from acmd import get_tool, Server

LS_RESPONSE = {
    'tasks': [
        {
            'id': 'task_id_4711',
            'dst': '/content/dam/something',
            "src": "http://admin:admin@localhost:4503/crx/server/-/jcr:root/content/dam/something",
            'status': {
                'state': 'RUNNING'
            }
        },
        {
            'id': 'task_id_4712',
            'dst': '/content/dam/something_else',
            "src": "http://admin:admin@localhost:4503/crx/server/-/jcr:root/content/dam/something",
            'status': {
                'state': 'CREATED'
            }
        }

    ]
}


@urlmatch(netloc='localhost:4502', method='GET')
def get_service_mock(url, request):
    if url.path == '/system/jackrabbit/filevault/rcp':
        return json.dumps(LS_RESPONSE)
    else:
        raise Exception(url.path)


posted_data = None



def tabbed(lines):
    lines = ['\t'.join(l) for l in lines]
    return '\n'.join(lines) + '\n'


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rcp_ls(stderr, stdout):
    with HTTMock(get_service_mock):
        tool = get_tool('rcp')
        server = Server('localhost')
        status = tool.execute(server, ['ls'])
        eq_(0, status)
        lines = [
            ['task_id_4711', 'localhost:4503', '/content/dam/something', 'RUNNING'],
            ['task_id_4712', 'localhost:4503', '/content/dam/something_else', 'CREATED']
        ]
        eq_(tabbed(lines), stdout.getvalue())
        eq_('', stderr.getvalue())


@urlmatch(netloc='localhost:4502', method='POST')
def post_service_mock(url, request):
    global posted_data

    if url.path == '/system/jackrabbit/filevault/rcp':
        posted_data = json.loads(request.body)
        return {
            'status_code': 201,
            'content': '{"status": "ok", "id": "rcp-0ed9f8"}'
        }

    else:
        raise Exception("Unexpected post uri {}".format(url))


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rcp_create(stderr, stdout):
    with HTTMock(post_service_mock):
        tool = get_tool('rcp')
        server = Server('localhost')
        status = tool.execute(server, ['rcp', 'create', '-s', 'other-host:4502', '-c', 'user:pass', '/content/dam/data'])

        eq_('http://user:pass@other-host:4502/crx/-/jcr:root/content/dam/data', posted_data['src'])

        eq_(0, status)
        eq_('rcp-0ed9f8\n', stdout.getvalue())
        eq_('', stderr.getvalue())
