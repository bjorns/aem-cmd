# coding: utf-8
from StringIO import StringIO
from mock import patch
from httmock import urlmatch, HTTMock
from nose.tools import eq_
from acmd.tools import packages
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
