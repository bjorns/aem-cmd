# coding: utf-8
from mock import patch
from httmock import urlmatch, HTTMock
from nose.tools import eq_
from acmd import tool_repo, Server

from test_utils.console import unordered_list
from test_utils.compat import StringIO


def test_tool_registration():
    tool = tool_repo.get_tool('search')
    assert tool is not None


@urlmatch(netloc='localhost:4502', path="/bin/querybuilder.json")
def service_mock(url, request):
    with open('tests/test_data/query_result.json') as f:
        return f.read()


EXPECTED_LIST = {
    "/content/paths/hit0",
    "/content/paths/hit1",
    "/content/paths/hit2"
}


@patch('sys.stdout', new_callable=StringIO)
def test_list_bundles(stdout):
    with HTTMock(service_mock):
        tool = tool_repo.get_tool('search')
        server = Server('localhost')
        tool.execute(server, ['search', '--path=/content', '--limit=3', 'foo=bar'])
        eq_(EXPECTED_LIST, unordered_list(stdout.getvalue()))
