# coding: utf-8
import json
from StringIO import StringIO
from httmock import urlmatch, HTTMock

from nose.tools import eq_
from mock import patch

from acmd import get_tool, Server

LS_RESPONSE = {
    'tasks': [
        {
            'id': 'task_id_4711',
            'dst': '/content/dam/something',
            'status': {
                'state': 'RUNNING'
            }
        },
        {
            'id': 'task_id_4712',
            'dst': '/content/dam/something_else',
            'status': {
                'state': 'CREATED'
            }
        }

    ]
}


@urlmatch(netloc='localhost:4502', method='GET')
def service_mock(url, request):
    if url.path == '/system/jackrabbit/filevault/rcp':
        return json.dumps(LS_RESPONSE)
    else:
        raise Exception(url.path)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rcp_ls(stderr, stdout):
    with HTTMock(service_mock):
        tool = get_tool('rcp')
        server = Server('localhost')
        status = tool.execute(server, ['ls'])
        eq_(0, status)
        eq_('task_id_4711\t/content/dam/something\tRUNNING\ntask_id_4712\t/content/dam/something_else\tCREATED\n', stdout.getvalue())
        eq_('', stderr.getvalue())
