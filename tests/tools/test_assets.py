# coding: utf-8
import json
import shutil
import tempfile
from StringIO import StringIO

from httmock import urlmatch, HTTMock
from mock import patch
from nose.tools import eq_

from acmd import Server, OK
from acmd.tools.assets import AssetsTool, flatten_properties, parse_tag, parse_tags, merge_tags
from tests.assets.mock_service import MockAssetsService, MockAssetsHttpService
from tests.workflow.mock_service import MockWorkflowHttpService, MockWorkflowsService


class RecordingHttpService(object):
    def __init__(self):
        self.req_log = []

    @urlmatch(netloc='localhost:4502', method='POST')
    def __call__(self, _, request):
        self.req_log.append(request)

        return {'status_code': 200,
                'content': ''}


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_import_asset_file(stderr, stdout):
    http_service = RecordingHttpService()

    lock_dir = tempfile.mkdtemp()
    with HTTMock(http_service):
        tool = AssetsTool()
        server = Server('localhost')
        status = tool.execute(server, ['assets', 'import', 'tests/test_data/assets/logo.jpg'])

    eq_('', stderr.getvalue())
    eq_(stdout.getvalue(), 'tests/test_data/assets/logo.jpg -> /content/dam/assets\n')
    eq_(OK, status)

    eq_(2, len(http_service.req_log))
    eq_(http_service.req_log[0].url, 'http://localhost:4502/content/dam/assets')
    eq_(http_service.req_log[1].url, 'http://localhost:4502/content/dam/assets.createasset.html')

    shutil.rmtree(lock_dir)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_import_asset_directory(stderr, stdout):
    http_service = RecordingHttpService()

    lock_dir = tempfile.mkdtemp()
    with HTTMock(http_service):
        tool = AssetsTool()
        server = Server('localhost')
        status = tool.execute(server, ['assets', 'import', 'tests/test_data/assets'])

    eq_('', stderr.getvalue())

    lines = stdout.getvalue().split('\n')
    eq_(4, len(lines))
    eq_(lines[0], 'tests/test_data/assets/logo.jpg -> /content/dam/assets')
    eq_(lines[1], 'tests/test_data/assets/subdir/graph.jpg -> /content/dam/assets/subdir')
    eq_(lines[2], 'tests/test_data/assets/subdir/graph2.jpg -> /content/dam/assets/subdir')
    eq_(OK, status)

    eq_(5, len(http_service.req_log))
    eq_(http_service.req_log[0].url, 'http://localhost:4502/content/dam/assets')
    eq_(http_service.req_log[1].url, 'http://localhost:4502/content/dam/assets.createasset.html')
    eq_(http_service.req_log[2].url, 'http://localhost:4502/content/dam/assets/subdir')
    eq_(http_service.req_log[3].url, 'http://localhost:4502/content/dam/assets/subdir.createasset.html')
    # Skipped creating subdir for the second file
    eq_(http_service.req_log[4].url, 'http://localhost:4502/content/dam/assets/subdir.createasset.html')

    shutil.rmtree(lock_dir)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_dry_run_import_asset_directory(stderr, stdout):
    http_service = RecordingHttpService()
    eq_([], http_service.req_log)

    lock_dir = tempfile.mkdtemp()
    with HTTMock(http_service):
        tool = AssetsTool()
        server = Server('localhost')
        status = tool.execute(server, ['assets', '--dry-run', 'import',
                                       'tests/test_data/assets'])

    eq_('', stderr.getvalue())

    lines = stdout.getvalue().split('\n')
    eq_(4, len(lines))
    eq_(lines[0], 'tests/test_data/assets/logo.jpg -> /content/dam/assets')
    eq_(lines[1], 'tests/test_data/assets/subdir/graph.jpg -> /content/dam/assets/subdir')
    eq_(lines[2], 'tests/test_data/assets/subdir/graph2.jpg -> /content/dam/assets/subdir')

    eq_(OK, status)

    eq_([], http_service.req_log)
    shutil.rmtree(lock_dir)


def test_flatten_properties():
    eq_({}, flatten_properties({}))
    eq_({'foobar': 3}, flatten_properties({'foobar': 3}))
    eq_({'foobar/baz': 3, 'foobar/quiz': 4},
        flatten_properties({'foobar': {'baz': 3, 'quiz': 4}}))


def test_parse_tag():
    status, key, val = parse_tag("key=value")
    eq_(OK, status)
    eq_('key', key)
    eq_('value', val)
    status, key, val = parse_tag("key2=val\=ue")
    eq_(OK, status)
    eq_('key2', key)
    eq_('val=ue', val)


def test_parse_tags():
    status, data = parse_tags('key1=val1,key2=val2')
    eq_(OK, status)
    eq_({'key1': 'val1', 'key2': 'val2'}, data)


def test_merge_tags():
    data = merge_tags({'key1': ['val1']}, {'key2': 'val2'})
    eq_({'key1': ['val1'], 'key2': ['val2']}, data)
    data = merge_tags({'key1': ['val1']}, {'key1': 'val2'})
    eq_({'key1': ['val1', 'val2']}, data)
    data = merge_tags({'key1': ['val1']}, {'key1': ['val2', 'val3']})
    eq_({'key1': ['val1', 'val2', 'val3']}, data)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_tag_asset(stdout, stderr):
    service = MockAssetsService()
    service.add_folder('/', 'hosts')
    service.add_asset('/hosts', 'bernard.jpg')

    http_service = MockAssetsHttpService(service)
    eq_([], http_service.request_log)

    with HTTMock(http_service):
        tool = AssetsTool()
        server = Server('localhost')
        status = tool.execute(server, ['assets', 'tag', 'type=westworld:type/secret',
                                       '/hosts/bernard.jpg'])

    eq_('', stderr.getvalue())
    eq_('', stdout.getvalue())
    eq_(OK, status)

    eq_(2, len(http_service.request_log))
    eq_(('GET', '/api/assets/hosts/bernard.jpg.json'), typeof(http_service.request_log[0]))
    eq_(('PUT', '/api/assets/hosts/bernard.jpg'), typeof(http_service.request_log[1]))
    eq_({u'class': u'asset', u'properties': {u'type': [u'westworld:type/secret']}},
        json.loads(http_service.request_log[1].body))


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
@patch('sys.stdin', StringIO("/hosts/bernard.jpg\n/hosts/abernathy.jpg\n"))
def test_tag_asset_from_stdin(stdout, stderr):
    service = MockAssetsService()
    service.add_folder('/', 'hosts')
    service.add_asset('/hosts', 'bernard.jpg')
    service.add_asset('/hosts', 'abernathy.jpg')

    http_service = MockAssetsHttpService(service)
    eq_([], http_service.request_log)

    with HTTMock(http_service):
        tool = AssetsTool()
        server = Server('localhost')
        status = tool.execute(server, ['assets', 'tag', 'type=westworld:type/secret'])

    eq_('', stderr.getvalue())
    eq_('', stdout.getvalue())
    eq_(OK, status)

    eq_(4, len(http_service.request_log))
    eq_(('GET', '/api/assets/hosts/bernard.jpg.json'), typeof(http_service.request_log[0]))
    eq_(('PUT', '/api/assets/hosts/bernard.jpg'), typeof(http_service.request_log[1]))
    eq_({u'class': u'asset', u'properties': {u'type': [u'westworld:type/secret']}},
        json.loads(http_service.request_log[1].body))
    eq_(('GET', '/api/assets/hosts/abernathy.jpg.json'), typeof(http_service.request_log[2]))
    eq_(('PUT', '/api/assets/hosts/abernathy.jpg'), typeof(http_service.request_log[3]))
    eq_({u'class': u'asset', u'properties': {u'type': [u'westworld:type/secret']}},
        json.loads(http_service.request_log[3].body))



def typeof(request):
    return request.method, request.path_url


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_touch_asset(stderr, stdout):
    service = MockWorkflowsService()
    http_service = MockWorkflowHttpService(service)
    eq_([], http_service.request_log)

    with HTTMock(http_service):
        tool = AssetsTool()
        server = Server('localhost')
        status = tool.execute(server, ['assets', 'touch', '/hosts/bernard.jpg'])

    eq_('', stderr.getvalue())
    eq_('/content/dam/hosts/bernard.jpg/jcr:content/renditions/original\n', stdout.getvalue())
    eq_(OK, status)

    eq_(1, len(http_service.request_log))
    eq_(('POST', '/etc/workflow/instances'), typeof(http_service.request_log[0]))
    eq_([], service.instances)
