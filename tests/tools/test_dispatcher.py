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


@urlmatch(netloc='localhost', path='/dispatcher/invalidate.cache', method='GET')
def broken_service(url, request):
    return "Something went wrong\n"
