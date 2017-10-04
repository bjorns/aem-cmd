# coding: utf-8
import json

from mock import patch
from httmock import urlmatch, HTTMock
from nose.tools import eq_, ok_

from acmd import tool_repo, Server, USER_ERROR, SERVER_ERROR
from acmd.tools import init_default_tools

from test_utils.compat import StringIO

init_default_tools()


@urlmatch(netloc='localhost:4502', method='POST')
def service_mock(url, request):
    eq_('script=println+%22foo%22%0Areturn+0', request.body)
    with open('tests/test_data/groovy_script_response.json') as f:
        return f.read()


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_missing_file_param(stderr, stdout):
    tool = tool_repo.get_tool('groovy')
    server = Server('localhost')
    status = tool.execute(server, ['groovy'])
    eq_(USER_ERROR, status)
    ok_(stdout.getvalue().startswith('Usage: acmd groovy'))
    eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_execute(stderr, stdout):
    with HTTMock(service_mock):
        tool = tool_repo.get_tool('groovy')
        server = Server('localhost')
        status = tool.execute(server, ['groovy', 'tests/test_data/script.groovy'])
        eq_(0, status)
        eq_('foo\n',
            stdout.getvalue())
        eq_('', stderr.getvalue())


EXPECTED_OUT = {
    "outputText": "foo\n",
    "stacktraceText": "",
    "executionResult": "0",
    "runningTime": "00:00:00.001"
}


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_execute_raw_output(stderr, stdout):
    with HTTMock(service_mock):
        tool = tool_repo.get_tool('groovy')
        server = Server('localhost')
        status = tool.execute(server, ['groovy', '--raw', 'tests/test_data/script.groovy'])
        eq_(0, status)
        eq_(EXPECTED_OUT,
            json.loads(stdout.getvalue()))
        eq_('', stderr.getvalue())


@urlmatch(netloc='localhost:4502', method='POST')
def broken_service(url, request):
    eq_('script=println+%22foo%22%0Areturn+0', request.body)
    return {'status_code': 500, 'content': 'error message'}


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_error_response(stderr, stdout):
    with HTTMock(broken_service):
        tool = tool_repo.get_tool('groovy')
        server = Server('localhost')
        status = tool.execute(server, ['groovy', 'tests/test_data/script.groovy'])
        eq_(SERVER_ERROR, status)
        eq_('',
            stdout.getvalue())
        eq_('error: Failed to run script tests/test_data/script.groovy: error message\n', stderr.getvalue())


@urlmatch(netloc='localhost:4502', method='POST')
def script_error_service(url, request):
    eq_('script=println+%22foo%22%0Areturn+0', request.body)
    with open('tests/test_data/groovy_script_error_response.json') as f:
        return str(f.read())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_script_error(stderr, stdout):
    with HTTMock(script_error_service):
        tool = tool_repo.get_tool('groovy')
        server = Server('localhost')
        status = tool.execute(server, ['groovy', 'tests/test_data/script.groovy'])
        eq_(SERVER_ERROR, status)
        eq_('', stdout.getvalue())
        eq_('Stacktrace Message', stderr.getvalue())
