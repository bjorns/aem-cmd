# coding: utf-8
from StringIO import StringIO
from mock import patch
from httmock import urlmatch, HTTMock
from nose.tools import eq_
from acmd.tools import bundles
from acmd import get_tool, Server

BUNDLE_LIST = """{
    "data": [
        {
            "category": "",
            "fragment": false,
            "id": 0,
            "name": "System Bundle",
            "state": "Active",
            "stateRaw": 32,
            "symbolicName": "org.apache.felix.framework",
            "version": "4.2.0"
        },
        {
            "category": "",
            "fragment": false,
            "id": 176,
            "name": "Abdera Client",
            "state": "Active",
            "stateRaw": 32,
            "symbolicName": "org.apache.abdera.client",
            "version": "1.0.0.R783018"
        },
        {
            "category": "",
            "fragment": false,
            "id": 177,
            "name": "Abdera Core",
            "state": "Active",
            "stateRaw": 32,
            "symbolicName": "org.apache.abdera.core",
            "version": "1.0.0.R783018"
        }
    ],
    "s": [
        329,
        320,
        9,
        0,
        0
    ],
    "status": "Bundle information: 329 bundles in total - all 329 bundles active."
}"""


def test_tool_registration():
    tool = get_tool('bundles')
    assert tool is not None

@urlmatch(netloc='localhost:4502', path='/system/console/bundles.json')
def bundles_mock(url, request):
    return BUNDLE_LIST

EXPECTED_LIST = """org.apache.felix.framework\t4.2.0\tActive
org.apache.abdera.client\t1.0.0.R783018\tActive
org.apache.abdera.core\t1.0.0.R783018\tActive
"""

@patch('sys.stdout', new_callable=StringIO)
def test_list_bundles(stdout):
    with HTTMock(bundles_mock):
        tool = bundles.BundlesTool()
        server = Server('localhost')

        tool.execute(server, ['bundles', 'list'])
        eq_(EXPECTED_LIST, stdout.getvalue())
