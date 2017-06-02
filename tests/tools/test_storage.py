# coding: utf-8
from mock import patch
from httmock import urlmatch, HTTMock

from nose.tools import eq_

from acmd.tools import storage
from acmd import tool_repo, Server

from test_utils.compat import StringIO


@urlmatch(netloc='localhost:4502',
          path='/system/console/jmx/com.adobe.granite:type=Repository/op/startTarOptimization/',
          method='POST')
def mock_optimize_service(url, request):
    return "optimize started"


@patch('sys.stdout', new_callable=StringIO)
def test_optimize_storage(stdout):
    with HTTMock(mock_optimize_service):
        tool = storage.DatastoreTool()
        server = Server('localhost')
        tool.execute(server, ['storage', '--raw', 'optimize'])
        eq_('optimize started', stdout.getvalue())


@urlmatch(netloc='localhost:4502',
          path='/system/console/jmx/com.adobe.granite:type=Repository/op/runDataStoreGarbageCollection/java.lang.Boolean',
          method='POST')
def mock_gc_service(url, request):
    return "gc started"


@patch('sys.stdout', new_callable=StringIO)
def test_storage_gc(stdout):
    with HTTMock(mock_gc_service):
        tool = tool_repo.get_tool('storage')
        server = Server('localhost')
        tool.execute(server, ['storage', '--raw', 'gc'])
        eq_('gc started', stdout.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_print_help(stdout, stderr):
    tool = tool_repo.get_tool('storage')
    server = Server('localhost')
    tool.execute(server, ['storage'])
    eq_('', stdout.getvalue())
    eq_('Usage: acmd storage [options] optimize|gc', stderr.getvalue().split('\n')[0])
