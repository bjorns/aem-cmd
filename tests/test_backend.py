# coding: utf-8
from acmd import OK

from nose.tools import eq_, ok_

from httmock import urlmatch, HTTMock

from acmd.backend import RESULT_FIELD, OUTPUT_FIELD, STACKTRACE_FIELD
from acmd.backend import _clean_output, execute
from acmd.server import Server


def test_clean_output():
    data = {
        'result': 0,
        'exceptionStackTrace': 'stacktrace data',
        'output': 'output data'
    }

    clean_data = _clean_output(data)
    eq_(0, clean_data[RESULT_FIELD])
    eq_('output data', clean_data[OUTPUT_FIELD])
    eq_('stacktrace data', clean_data[STACKTRACE_FIELD])


@urlmatch(netloc='localhost:4502', method='POST')
def service_mock(_, request):
    eq_('script=println+%22foo%22%0Areturn+0', request.body)
    with open('tests/test_data/groovy_script_response.json', 'rb') as f:
        return f.read()


def test_execute():
    with HTTMock(service_mock):
        server = Server('localhost')
        f = open('tests/test_data/script.groovy')
        status, data = execute(server, f.read(), ['groovy'])
        eq_(OK, status)
        eq_(u'foo\n', data[OUTPUT_FIELD])
        eq_(u'0', data[RESULT_FIELD])
        ok_(STACKTRACE_FIELD not in data)
