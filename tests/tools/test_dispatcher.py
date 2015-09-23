# coding: utf-8
from StringIO import StringIO
from acmd import get_tool, Server

from nose.tools import eq_
from mock import patch
from httmock import urlmatch, HTTMock


@urlmatch(netloc='localhost', path='/dispatcher/invalidate.cache', method='GET')
def service_mock(url, request):
    eq_('/dispatcher/invalidate.cache', url.path)
    eq_('GET', request.method)
    return "<H1>OK</H1>\n"


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_clear_cache(stderr, stdout):
    tool = get_tool('dispatcher')
    server = Server('localhost')
    with HTTMock(service_mock):
        tool.execute(server, ['dispatcher', 'clear'])
    eq_("OK\n", stdout.getvalue())
    eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_clear_cache_with_explicit_dispatcher(stderr, stdout):
    tool = get_tool('dispatcher')
    server = Server('localhost', host='http://doesntexist', dispatcher="http://localhost")
    with HTTMock(service_mock):
        tool.execute(server, ['dispatcher', 'clear'])
    eq_("OK\n", stdout.getvalue())
    eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_clear_cache_with_raw_output(stderr, stdout):
    tool = get_tool('dispatcher')
    server = Server('localhost', host='aslkadlkjasd', dispatcher="http://localhost")
    with HTTMock(service_mock):
        tool.execute(server, ['dispatcher', 'clear', '--raw'])
    eq_("<H1>OK</H1>\n\n", stdout.getvalue())
    eq_('', stderr.getvalue())


@urlmatch(netloc='localhost', path='/dispatcher/invalidate.cache', method='GET')
def broken_service(url, request):
    return "Something went wrong\n"


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_clear_cache_with_broken_service(stderr, stdout):
    tool = get_tool('dispatcher')
    server = Server('localhost', host='aslkadlkjasd', dispatcher="http://localhost")
    with HTTMock(broken_service):
        tool.execute(server, ['dispatcher', 'clear'])
    eq_('', stdout.getvalue())
    eq_("error: Failed to validate response 'Something went wrong'\n", stderr.getvalue())
