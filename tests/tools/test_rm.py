# coding: utf-8
from mock import patch
from httmock import urlmatch, HTTMock
from nose.tools import eq_

from acmd import tool_repo, Server

from test_utils.compat import StringIO

@urlmatch(netloc='localhost:4502', method='DELETE')
def service_rm(url, request):
    return {
        'content': '',
        'status_code': 204
    }


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_rm(stderr, stdout):
    with HTTMock(service_rm):
        tool = tool_repo.get_tool('rm')
        server = Server('localhost')
        status = tool.execute(server, ['rm', '/content/path/node'])
        eq_(0, status)
        eq_('/content/path/node\n', stdout.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
@patch('sys.stdin', new=StringIO('/content/path/node\n'))
def test_rm_stdin(stderr, stdout):
    with HTTMock(service_rm):
        tool = tool_repo.get_tool('rm')
        server = Server('localhost')
        status = tool.execute(server, ['rm'])
        eq_(0, status)
        eq_('/content/path/node\n', stdout.getvalue())
