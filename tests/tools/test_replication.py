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



EXPECTED = """/content/catalog/products
/content/catalog/products/product4711
/content/catalog/products/product4712
"""

@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_activate(stderr, stdout):
    with HTTMock(mock_replication_service):
        tool = get_tool('replication')
        server = Server('localhost')
        tool.execute(server, ['replication', 'activate', '/content/catalog'])
        eq_(EXPECTED, stdout.getvalue())
        eq_('', stderr.getvalue())
