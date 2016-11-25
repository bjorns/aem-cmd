# coding: utf-8
import re
import shutil
import tempfile
from StringIO import StringIO

from httmock import urlmatch, HTTMock
from mock import patch
from nose.tools import eq_, ok_

from acmd import Server, OK
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
    _is_valid_upload_line(stdout.getvalue(),
                          ['2016-11-25 13:12:01', '1/1', 'tests/test_data/assets/logo.jpg -> /content/dam/assets',
                           '0.0192'])
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
    _is_valid_upload_line(lines[0],
                          ['2016-11-25 13:12:01', '1/3', 'tests/test_data/assets/logo.jpg -> /content/dam/assets',
                           '0.0192'])
    _is_valid_upload_line(lines[1],
                          ['2016-11-25 13:12:01', '2/3',
                           'tests/test_data/assets/subdir/graph.jpg -> /content/dam/assets/subdir',
                           '0.0192'])
    _is_valid_upload_line(lines[2],
                          ['2016-11-25 13:12:01', '3/3',
                           'tests/test_data/assets/subdir/graph2.jpg -> /content/dam/assets/subdir',
                           '0.0192'])

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
    eq_([], http_service.req_log)

    lock_dir = tempfile.mkdtemp()
    with HTTMock(http_service):
        tool = AssetsTool()
        server = Server('localhost')
        status = tool.execute(server, ['assets', '--dry-run', '--lock-dir={}'.format(lock_dir), 'import',
                                       'tests/test_data/assets'])

    eq_('', stderr.getvalue())

    lines = stdout.getvalue().split('\n')
    eq_(4, len(lines))
    _is_valid_upload_line(lines[0],
                          ['2016-11-25 13:12:01', '1/3', 'tests/test_data/assets/logo.jpg -> /content/dam/assets',
                           '0.0192'])
    _is_valid_upload_line(lines[1],
                          ['2016-11-25 13:12:01', '2/3',
                           'tests/test_data/assets/subdir/graph.jpg -> /content/dam/assets/subdir',
                           '0.0192'])
    _is_valid_upload_line(lines[2],
                          ['2016-11-25 13:12:01', '3/3',
                           'tests/test_data/assets/subdir/graph2.jpg -> /content/dam/assets/subdir',
                           '0.0192'])

    eq_(OK, status)

    eq_([], http_service.req_log)
    shutil.rmtree(lock_dir)


def _is_valid_upload_line(line, template):
    line_parts = line.split('\t')
    _is_date(line_parts[0])
    eq_(template[1:-1], line_parts[1:-1])
    _is_upload_time(line_parts[-1])


def _is_date(data):
    pattern = re.compile('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
    ok_(pattern.match(data) is not None)


def _is_upload_time(data):
    pattern = re.compile('\d+\.\d+')
    ok_(pattern.match(data) is not None)
