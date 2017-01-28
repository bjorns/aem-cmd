# coding: utf-8
import json
import shutil
import tempfile
from StringIO import StringIO

from httmock import urlmatch, HTTMock
from mock import patch
from nose.tools import eq_

from acmd import Server, OK
from acmd.tools.assets import AssetsTool, get_tags
from tests.assets import MockAssetsHttpService, MockAssetsService


class RecordingHttpService(object):
    def __init__(self):
        self.req_log = []

    @urlmatch(netloc='localhost:4502', method='POST')
    def __call__(self, url, request):
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


PROPS = {
    "cq:name": "robot.jpg",
    "cq:parentPath": "/content/dam/pink",
    "name": "robot.jpg",
    "dc:title": "My Asset",
    "related": {},
    "srn:paging": {
        "total": 0,
        "limit": 20,
        "offset": 0
    },
    "metadata": {
        "name": "Bernard",
        "roles": [
            "Host",
            "Management"
        ],
        "dc:modified": "2017-01-27T21:08:05.465Z",
        "dc:format": "image/jpeg"
    }
}


def test_get_tags():
    eq_("robot.jpg", get_tags(PROPS, "name"))
    eq_("Bernard", get_tags(PROPS, "metadata/name"))
    eq_([], get_tags(PROPS, "metadata/doesntexist"))


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
        status = tool.execute(server, ['assets', 'tag', 'type', 'westworld:type/secret',
                                       '/hosts/bernard.jpg'])

    eq_('', stderr.getvalue())
    eq_('', stdout.getvalue())
    eq_(OK, status)

    eq_(2, len(http_service.request_log))
    eq_(('GET', '/api/assets/hosts/bernard.jpg.json'), typeof(http_service.request_log[0]))
    eq_(('PUT', '/api/assets/hosts/bernard.jpg'), typeof(http_service.request_log[1]))
    eq_({u'class': u'asset', u'properties': {u'type': [u'westworld:type/secret']}},
        json.loads(http_service.request_log[1].body))


def typeof(request):
    return request.method, request.path_url
