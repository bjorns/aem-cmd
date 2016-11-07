# coding: utf-8
import json
import tempfile
import shutil
import cgi

from StringIO import StringIO
from httmock import urlmatch, HTTMock
from mock import patch
from nose.tools import eq_

from acmd import get_tool, Server, OK
from acmd.tools.assets import AssetsTool


class MockAssetService(object):
    def __init__(self):
        self.files = dict()

    def add_file(self, path, data):
        assert path not in self.files
        self.files[path] = data


class MockHttpService(object):
    def __init__(self, asset_service=None):
        self.asset_service = asset_service if asset_service is not None else MockAssetService()
        self.req_log = []

    @urlmatch(netloc='localhost:4502', method='POST')
    def __call__(self, url, request):
        self.req_log.append(request)

        return {'status_code': 200,
                'content': ''}


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_import_asset_file(stderr, stdout):
    http_service = MockHttpService()

    lock_dir = tempfile.mkdtemp()
    with HTTMock(http_service):
        tool = AssetsTool()
        server = Server('localhost')
        status = tool.execute(server, ['assets', '--lock-dir={}'.format(lock_dir),
                                       'import', 'tests/test_data/assets/logo.jpg'])

    eq_('', stderr.getvalue())
    eq_('1/1 tests/test_data/assets/logo.jpg -> /content/dam/assets\n', stdout.getvalue())
    eq_(OK, status)

    eq_(2, len(http_service.req_log))
    eq_(http_service.req_log[0].url, 'http://localhost:4502/content/dam/assets')
    eq_(http_service.req_log[1].url, 'http://localhost:4502/content/dam/assets.createasset.html')

    shutil.rmtree(lock_dir)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_import_asset_directory(stderr, stdout):
    http_service = MockHttpService()

    lock_dir = tempfile.mkdtemp()
    with HTTMock(http_service):
        tool = AssetsTool()
        server = Server('localhost')
        status = tool.execute(server, ['assets', '--lock-dir={}'.format(lock_dir), 'import', 'tests/test_data/assets'])

    eq_('', stderr.getvalue())

    lines = stdout.getvalue().split('\n')
    eq_(4, len(lines))
    eq_(lines[0], '1/3 tests/test_data/assets/logo.jpg -> /content/dam/assets')
    eq_(lines[1], '2/3 tests/test_data/assets/subdir/graph.jpg -> /content/dam/assets/subdir')
    eq_(lines[2], '3/3 tests/test_data/assets/subdir/graph2.jpg -> /content/dam/assets/subdir')
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
    http_service = MockHttpService()
    eq_(0, len(http_service.req_log))

    lock_dir = tempfile.mkdtemp()
    with HTTMock(http_service):
        tool = AssetsTool()
        server = Server('localhost')
        status = tool.execute(server, ['assets', '--dry-run', '--lock-dir={}'.format(lock_dir), 'import', 'tests/test_data/assets'])

    eq_('', stderr.getvalue())

    lines = stdout.getvalue().split('\n')
    eq_(4, len(lines))
    eq_(lines[0], '1/3 tests/test_data/assets/logo.jpg -> /content/dam/assets')
    eq_(lines[1], '2/3 tests/test_data/assets/subdir/graph.jpg -> /content/dam/assets/subdir')
    eq_(lines[2], '3/3 tests/test_data/assets/subdir/graph2.jpg -> /content/dam/assets/subdir')
    eq_(OK, status)

    eq_(0, len(http_service.req_log))
    shutil.rmtree(lock_dir)


