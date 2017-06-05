# coding: utf-8
import json
import shutil
import tempfile

from httmock import urlmatch, HTTMock
from mock import patch
from nose.tools import eq_

from acmd import Server, OK
from acmd.tools.asset_tool import AssetTool, flatten_properties, parse_tag, parse_tags, merge_tags, merge_tag_field

from test_utils.mocks.workflow import MockWorkflowHttpService, MockWorkflowsService
from test_utils.mocks.dam import MockAssetsHttpService, MockAssetsService
from test_utils.compat import StringIO


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
        tool = AssetTool()
        server = Server('localhost')
        status = tool.execute(server, ['asset', 'import', 'tests/test_data/assets/logo.jpg'])

    eq_('', stderr.getvalue())
    eq_(stdout.getvalue(), 'tests/test_data/assets/logo.jpg -> /assets\n')
    eq_(OK, status)

    eq_(2, len(http_service.req_log))
    eq_(http_service.req_log[0].url, 'http://localhost:4502/api/assets/assets')
    eq_(http_service.req_log[1].url, 'http://localhost:4502/api/assets/assets/logo.jpg')

    shutil.rmtree(lock_dir)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_import_asset_directory(stderr, stdout):
    http_service = RecordingHttpService()

    lock_dir = tempfile.mkdtemp()
    with HTTMock(http_service):
        tool = AssetTool()
        server = Server('localhost')
        status = tool.execute(server, ['assets', 'import', 'tests/test_data/assets'])

    eq_('', stderr.getvalue())

    lines = stdout.getvalue().split('\n')
    eq_(4, len(lines))
    eq_(lines[0], 'tests/test_data/assets/logo.jpg -> /assets')
    eq_(lines[1], 'tests/test_data/assets/subdir/graph.jpg -> /assets/subdir')
    eq_(lines[2], 'tests/test_data/assets/subdir/graph2.jpg -> /assets/subdir')
    eq_(OK, status)

    eq_(5, len(http_service.req_log))
    eq_(http_service.req_log[0].url, 'http://localhost:4502/api/assets/assets')
    eq_(http_service.req_log[1].url, 'http://localhost:4502/api/assets/assets/logo.jpg')
    eq_(http_service.req_log[2].url, 'http://localhost:4502/api/assets/assets/subdir')
    eq_(http_service.req_log[3].url, 'http://localhost:4502/api/assets/assets/subdir/graph.jpg')
    # Skipped creating subdir for the second file
    eq_(http_service.req_log[4].url, 'http://localhost:4502/api/assets/assets/subdir/graph2.jpg')

    shutil.rmtree(lock_dir)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_dry_run_import_asset_directory(stderr, stdout):
    http_service = RecordingHttpService()
    eq_([], http_service.req_log)

    lock_dir = tempfile.mkdtemp()
    with HTTMock(http_service):
        tool = AssetTool()
        server = Server('localhost')
        status = tool.execute(server, ['assets', '--dry-run', 'import',
                                       'tests/test_data/assets'])

    eq_('', stderr.getvalue())

    lines = stdout.getvalue().split('\n')
    eq_(4, len(lines))
    eq_(lines[0], 'tests/test_data/assets/logo.jpg -> /assets')
    eq_(lines[1], 'tests/test_data/assets/subdir/graph.jpg -> /assets/subdir')
    eq_(lines[2], 'tests/test_data/assets/subdir/graph2.jpg -> /assets/subdir')

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
    eq_({'key1': ['val1'], 'key2': ['val2']}, data)


def test_merge_tags():
    data = merge_tags({'key1': ['val1']}, {'key2': ['val2']})
    eq_({'key1': ['val1'], 'key2': ['val2']}, data)
    data = merge_tags({'key1': ['val1']}, {'key1': ['val2']})
    eq_({'key1': ['val1', 'val2']}, data)
    data = merge_tags({'key1': ['val1']}, {'key1': ['val2', 'val3']})
    eq_({'key1': ['val1', 'val2', 'val3']}, data)


def test_merge_tag_field():
    eq_(['a', 'b', 'c'], merge_tag_field(['a', 'b'], ['c']))
    eq_(['a', 'b'], merge_tag_field(['a', 'b'], ['b']))


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_tag_asset(stderr, stdout):
    service = MockAssetsService()
    service.add_folder('/', 'hosts')
    service.add_asset('/hosts', 'bernard.jpg')

    http_service = MockAssetsHttpService(service)
    eq_([], http_service.request_log)

    with HTTMock(http_service):
        tool = AssetTool()
        server = Server('localhost')
        status = tool.execute(server, ['asset', 'tag', 'type=westworld:type/secret',
                                       '/hosts/bernard.jpg'])

    eq_('', stderr.getvalue())
    eq_('/hosts/bernard.jpg\n', stdout.getvalue())
    eq_(OK, status)

    eq_(2, len(http_service.request_log))
    eq_(('GET', '/api/assets/hosts/bernard.jpg.json'), typeof(http_service.request_log[0]))
    eq_(('PUT', '/api/assets/hosts/bernard.jpg'), typeof(http_service.request_log[1]))
    # body_data = json.loads(http_service.request_log[1].body)
    # eq_({u'class': u'asset', u'properties': {u'type': [u'westworld:type/secret'], u'name': u'bernard.jpg'}},
    #    json.loads(http_service.request_log[1].body))


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
@patch('sys.stdin', StringIO("/hosts/bernard.jpg\n/hosts/abernathy.jpg\n"))
def test_tag_asset_from_stdin(stderr, stdout):
    service = MockAssetsService()
    service.add_folder('/', 'hosts')
    service.add_asset('/hosts', 'bernard.jpg')
    service.add_asset('/hosts', 'abernathy.jpg')

    http_service = MockAssetsHttpService(service)
    eq_([], http_service.request_log)

    with HTTMock(http_service):
        tool = AssetTool()
        server = Server('localhost')
        status = tool.execute(server, ['asset', 'tag', 'type=westworld:type/secret'])

    eq_('', stderr.getvalue())
    eq_('/hosts/bernard.jpg\n/hosts/abernathy.jpg\n', stdout.getvalue())
    eq_(OK, status)

    eq_(4, len(http_service.request_log))
    eq_(('GET', '/api/assets/hosts/bernard.jpg.json'), typeof(http_service.request_log[0]))
    eq_(('PUT', '/api/assets/hosts/bernard.jpg'), typeof(http_service.request_log[1]))
    body_data = json.loads(http_service.request_log[1].body)
    eq_([u'westworld:type/secret'], body_data['properties']['type'])

    eq_(('GET', '/api/assets/hosts/abernathy.jpg.json'), typeof(http_service.request_log[2]))
    eq_(('PUT', '/api/assets/hosts/abernathy.jpg'), typeof(http_service.request_log[3]))
    body_data = json.loads(http_service.request_log[3].body)
    eq_([u'westworld:type/secret'], body_data['properties']['type'])


def typeof(request):
    return request.method, request.path_url


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_touch_asset(stderr, stdout):
    service = MockWorkflowsService()
    http_service = MockWorkflowHttpService(service)
    eq_([], http_service.request_log)

    with HTTMock(http_service):
        tool = AssetTool()
        server = Server('localhost')
        status = tool.execute(server, ['asset', 'touch', '/hosts/bernard.jpg'])

    eq_('', stderr.getvalue())
    eq_('/content/dam/hosts/bernard.jpg/jcr:content/renditions/original\n', stdout.getvalue())
    eq_(OK, status)

    eq_(1, len(http_service.request_log))
    eq_(('POST', '/etc/workflow/instances'), typeof(http_service.request_log[0]))
    eq_([], service.instances)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
@patch('sys.stdin', StringIO("/hosts/bernard.jpg\n/hosts/abernathy.jpg\n"))
def test_touch_assets_from_stdin(stderr, stdout):
    service = MockWorkflowsService()
    http_service = MockWorkflowHttpService(service)
    eq_([], http_service.request_log)

    with HTTMock(http_service):
        tool = AssetTool()
        server = Server('localhost')
        status = tool.execute(server, ['asset', 'touch'])

    eq_(OK, status)
    eq_('', stderr.getvalue())
    lines = stdout.getvalue().split('\n')
    eq_('/content/dam/hosts/bernard.jpg/jcr:content/renditions/original', lines[0])
    eq_('/content/dam/hosts/abernathy.jpg/jcr:content/renditions/original', lines[1])

    eq_(2, len(http_service.request_log))
    eq_(('POST', '/etc/workflow/instances'), typeof(http_service.request_log[0]))
    eq_([], service.instances)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_list_assets(stderr, stdout):
    service = MockAssetsService()
    service.add_folder('/', 'hosts')
    service.add_asset('/hosts', 'bernard.jpg')
    service.add_asset('/hosts', 'dolores.jpg')

    http_service = MockAssetsHttpService(service)
    eq_([], http_service.request_log)

    with HTTMock(http_service):
        tool = AssetTool()
        server = Server('localhost')
        status = tool.execute(server, ['asset', 'ls', '/hosts'])

    eq_(OK, status)
    eq_('', stderr.getvalue())

    lines = stdout.getvalue().split('\n')
    eq_('bernard.jpg', lines[0])
    eq_('dolores.jpg', lines[1])

    eq_(1, len(http_service.request_log))
    eq_(('GET', '/api/assets/hosts.json'), typeof(http_service.request_log[0]))


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_list_assets(stderr, stdout):
    service = MockAssetsService()
    service.add_folder('/', 'hosts')
    service.add_asset('/hosts', 'bernard.jpg')
    service.add_asset('/hosts', 'dolores.jpg')
    service.add_folder('/', 'staff')
    service.add_asset('/staff', 'bernard.jpg')
    service.add_asset('/staff', 'elsie.jpg')

    http_service = MockAssetsHttpService(service)
    eq_([], http_service.request_log)

    with HTTMock(http_service):
        tool = AssetTool()
        server = Server('localhost')
        status = tool.execute(server, ['asset', 'find', '/'])

    eq_(OK, status)

    eq_(3, len(http_service.request_log))
    eq_(('GET', '/api/assets/.json'), typeof(http_service.request_log[0]))

    eq_('', stderr.getvalue())
    lines = stdout.getvalue().split('\n')
    eq_(5, len(lines))
    eq_('/staff/bernard.jpg', lines[0])
    eq_('/staff/elsie.jpg', lines[1])
    eq_('/hosts/bernard.jpg', lines[2])
    eq_('/hosts/dolores.jpg', lines[3])

    eq_('', lines[4])
