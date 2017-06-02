# coding: utf-8
from mock import patch
from httmock import urlmatch, HTTMock

from nose.tools import eq_

from acmd.tools import bundle
from acmd import tool_repo, Server

from test_utils.compat import StringIO

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
    tool = tool_repo.get_tool('bundle')
    assert tool is not None


@urlmatch(netloc='localhost:4502', path='/system/console/bundles.json', method='GET')
def bundles_mock(url, request):
    return BUNDLE_LIST


EXPECTED_LIST = """org.apache.felix.framework\t4.2.0\tActive
org.apache.abdera.client\t1.0.0.R783018\tActive
org.apache.abdera.core\t1.0.0.R783018\tActive
"""


@patch('sys.stdout', new_callable=StringIO)
def test_list_bundles(stdout):
    with HTTMock(bundles_mock):
        tool = bundle.BundleTool()
        server = Server('localhost')

        tool.execute(server, ['bundle', 'list'])
        eq_(EXPECTED_LIST, stdout.getvalue())


_expected_action = None


@urlmatch(netloc='localhost:4502', path="/system/console/bundles/mock_bundle", method='POST')
def mock_bundle(url, request):
    eq_('action={}'.format(_expected_action), request.body)
    return '{"fragment":false,"stateRaw":4}' if _expected_action == 'stop' else '{"fragment":false,"stateRaw":32}'


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_stop_bundle(stderr, stdout):
    global _expected_action
    _expected_action = 'stop'
    with HTTMock(mock_bundle):
        tool = tool_repo.get_tool('bundle')
        server = Server('localhost')
        ret = tool.execute(server, ['bundle', 'stop', 'mock_bundle'])
        eq_('', stdout.getvalue())
        eq_('', stderr.getvalue())
        eq_(None, ret)

        ret = tool.execute(server, ['bundles', 'stop', '--raw', 'mock_bundle'])
        eq_('{"fragment":false,"stateRaw":4}\n', stdout.getvalue())
        eq_('', stderr.getvalue())
        eq_(None, ret)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_start_bundle(stderr, stdout):
    global _expected_action
    _expected_action = 'start'
    with HTTMock(mock_bundle):
        tool = tool_repo.get_tool('bundle')
        server = Server('localhost')
        ret = tool.execute(server, ['bundle', 'start', 'mock_bundle'])
        eq_('', stdout.getvalue())
        eq_('', stderr.getvalue())
        eq_(None, ret)

        ret = tool.execute(server, ['bundles', 'start', '--raw', 'mock_bundle'])
        eq_('{"fragment":false,"stateRaw":32}\n', stdout.getvalue())
        eq_('', stderr.getvalue())
        eq_(None, ret)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_bad_command(stderr, stdout):
    tool = tool_repo.get_tool('bundle')
    server = Server('localhost')
    ret = tool.execute(server, ['bundle', 'foobar'])
    eq_('', stdout.getvalue())
    eq_('error: Unknown bundle action foobar\n', stderr.getvalue())
    eq_(-2, ret)
