# coding: utf-8
from StringIO import StringIO

from mock import patch
from httmock import urlmatch, HTTMock
from nose.tools import eq_

from acmd import get_tool, Server


@urlmatch(netloc='localhost:4502', path='/etc/replication/treeactivation.html', method='POST')
def mock_replication_service(_, request):
    if 'cmd=activate' in request.body:
        with open('tests/test_data/activation_response.html', 'rb') as f:
            return f.read()
    else:
        raise Exception("Unknown command " + request.body)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_activate(stderr, stdout):
    with HTTMock(mock_replication_service):
        tool = get_tool('replication')
        server = Server('localhost')
        tool.execute(server, ['replication', 'activate', '/content/catalog'])
        eq_('Activated 130 of 130 resources in 4 seconds.\n', stdout.getvalue())
        eq_('', stderr.getvalue())
