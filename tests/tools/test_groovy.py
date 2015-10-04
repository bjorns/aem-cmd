# coding: utf-8
from StringIO import StringIO
from acmd import get_tool, Server, USER_ERROR, SERVER_ERROR

from mock import patch
from httmock import urlmatch, HTTMock
from nose.tools import eq_, ok_


@urlmatch(netloc='localhost:4502', method='POST')
def service_mock(url, request):
    eq_('script=println+%22foo%22%0Areturn+0', request.body)
    with open('tests/test_data/groovy_script_response.json', 'rb') as f:
        return f.read()


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_missing_file_param(stderr, stdout):
    tool = get_tool('groovy')
    server = Server('localhost')
    status = tool.execute(server, ['groovy'])
    eq_(USER_ERROR, status)
    ok_(stdout.getvalue().startswith('Usage: acmd groups'))
    eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_execute(stderr, stdout):
    with HTTMock(service_mock):
        tool = get_tool('groovy')
        server = Server('localhost')
        status = tool.execute(server, ['groovy', 'tests/test_data/script.groovy'])
        eq_(0, status)
        eq_('foo\n',
            stdout.getvalue())
        eq_('', stderr.getvalue())


EXPECTED_RAW_OUTPUT = '{\n    "outputText": "foo\\n", \n    "stacktraceText": "", \n    "executionResult": "0", \n    "runningTime": "00:00:00.001"\n}\n'

@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_execute_raw_output(stderr, stdout):
    with HTTMock(service_mock):
        tool = get_tool('groovy')
        server = Server('localhost')
        status = tool.execute(server, ['groovy', '--raw', 'tests/test_data/script.groovy'])
        eq_(0, status)
        eq_(EXPECTED_RAW_OUTPUT,
            stdout.getvalue())
        eq_('', stderr.getvalue())


@urlmatch(netloc='localhost:4502', method='POST')
def broken_service(url, request):
    eq_('script=println+%22foo%22%0Areturn+0', request.body)
    return {'status_code': 500, 'content': 'error message'}


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_error_response(stderr, stdout):
    with HTTMock(broken_service):
        tool = get_tool('groovy')
        server = Server('localhost')
        status = tool.execute(server, ['groovy', 'tests/test_data/script.groovy'])
        eq_(SERVER_ERROR, status)
        eq_('',
            stdout.getvalue())
        eq_('error: Failed to run script tests/test_data/script.groovy: error message\n', stderr.getvalue())


@urlmatch(netloc='localhost:4502', method='POST')
def script_error_service(url, request):
    eq_('script=println+%22foo%22%0Areturn+0', request.body)
    with open('tests/test_data/groovy_script_error_response.json', 'rb') as f:
        return f.read()


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_script_error(stderr, stdout):
    with HTTMock(script_error_service):
        tool = get_tool('groovy')
        server = Server('localhost')
        status = tool.execute(server, ['groovy', 'tests/test_data/script.groovy'])
        eq_(SERVER_ERROR, status)
        eq_('', stdout.getvalue())
        eq_('Stacktrace Message', stderr.getvalue())
