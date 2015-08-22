# coding: utf-8
from StringIO import StringIO
from mock import patch
from httmock import urlmatch, HTTMock
from nose.tools import eq_
from acmd import get_tool, Server

from acmd.tools import search


def test_tool_registration():
    tool = get_tool('search')
    assert tool is not None

@urlmatch(netloc='localhost:4502', path="/bin/querybuilder.json", query="path=%2Fcontent&1_property.value=bar&p.limit=3&1_property=foo")
def service_mock(url, request):
    with open('tests/test_data/query_result.json', 'rb') as f:
        return f.read()


EXPECTED_LIST = """/content/paths/hit0
/content/paths/hit1
/content/paths/hit2
"""

@patch('sys.stdout', new_callable=StringIO)
def test_list_bundles(stdout):
    with HTTMock(service_mock):
        tool = get_tool('search')
        server = Server('localhost')

        tool.execute(server, ['search', '--path=/content', '--limit=3', 'foo=bar'])
        eq_(EXPECTED_LIST, stdout.getvalue())
