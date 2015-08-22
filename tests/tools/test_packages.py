# coding: utf-8
from StringIO import StringIO
from mock import patch
from httmock import urlmatch, HTTMock
from nose.tools import eq_
from acmd.tools import packages
from acmd import get_tool, Server


def test_tool_registration():
    tool = get_tool('packages')
    assert tool is not None

@urlmatch(netloc='localhost:4502')
def packages_mock(url, request):
    with open('tests/test_data/packages_list.xml', 'rb') as f:
        return f.read()


EXPECTED_LIST = """adobe/granite\tcom.adobe.coralui.content\t1.6.5
adobe/granite\tcom.adobe.coralui.rte-cq5\t5.6.18
adobe/granite\tcom.adobe.granite.activitystreams.content\t0.0.12
"""

@patch('sys.stdout', new_callable=StringIO)
def test_list_bundles(stdout):
    with HTTMock(packages_mock):
        tool = packages.PackagesTool()
        server = Server('localhost')

        tool.execute(server, ['bundles', 'list'])
        eq_(EXPECTED_LIST, stdout.getvalue())
