# coding: utf-8
from StringIO import StringIO

from mock import patch
from httmock import urlmatch, HTTMock
from nose.tools import eq_

from acmd import get_tool, Server


@urlmatch(netloc='localhost:4502', method='POST')
def service_mock(url, request):
    eq_('prop1%40Delete=&prop0%40Delete=', request.body)
    return ""


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rmprop(stderr, stdout):
    with HTTMock(service_mock):
        tool = get_tool('rmprop')
        server = Server('localhost')
        status = tool.execute(server, ['rmprop', 'prop0,prop1', '/content/path/node'])
        eq_(0, status)
        eq_('/content/path/node\n', stdout.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
@patch('sys.stdin', new=StringIO("/path0\n/path1\n"))
def test_rmprop_stdin(stderr, stdout):
    with HTTMock(service_mock):
        tool = get_tool('rmprop')
        server = Server('localhost')
        status = tool.execute(server, ['rmprop', 'prop0,prop1'])
        eq_(0, status)
        eq_('/path0\n/path1\n', stdout.getvalue())

