# coding: utf-8
from nose.tools import eq_
from httmock import urlmatch


@urlmatch(netloc='localhost', path='/dispatcher/invalidate.cache', method='GET')
def service_mock(url, request):
    eq_('/dispatcher/invalidate.cache', url.path)
    eq_('GET', request.method)
    return "<H1>OK</H1>\n"


@urlmatch(netloc='localhost', path='/dispatcher/invalidate.cache', method='GET')
def broken_service(*_):
    return "Something went wrong\n"
