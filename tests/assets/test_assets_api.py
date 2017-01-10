# coding: utf-8
import json
from StringIO import StringIO

from httmock import urlmatch, HTTMock
from mock import patch
from nose.tools import eq_

import acmd.assets
import acmd.jcr.path
from acmd import Server, OK
from acmd.strings import remove_suffix, remove_prefix


class MockAssetsService(object):
    def __init__(self):
        self.repo = dict()
        self.repo['/'] = dict(
            type='assets/folder',
            name="/",
            parent=None,
            children=[],
            assets=[]
        )

    def add_asset(self, parent, name):
        path = acmd.jcr.path.join(parent, name)
        assert path not in self.repo

        asset = dict(
            type='assets/asset',
            name=name,
            parent=parent,
            path=path,
        )
        self.repo[path] = asset
        self.repo[parent]['assets'].append(name)

    def add_folder(self, parent, name):
        folder = dict(
            type='assets/folder',
            name=name,
            parent=parent,
            children=[],
            assets=[]
        )
        path = acmd.jcr.path.join(parent, name)
        self.repo[parent]['children'].append(path)
        self.repo[path] = folder

    def get(self, path):
        return self.repo[path]


class MockAssetsHttpService(object):
    def __init__(self, service):
        self.service = service
        self.request_log = []

    @urlmatch(netloc='localhost:4502')
    def __call__(self, url, request):
        self.request_log.append(request)
        if request.method == 'GET':
            service_path = self._get_api_path(url.path)
            data = self.service.get(service_path)
            return json.dumps(self._translate(data))
        else:
            raise Exception("Not implemented")

    @staticmethod
    def _get_api_path(path):
        return remove_suffix('.json', remove_prefix('/api/assets', path))

    def _translate(self, data):
        if data['type'] == 'assets/asset':
            return self._translate_asset(data)
        elif data['type'] == 'assets/folder':
            return self._translate_folder(data)
        else:
            raise Exception()

    @staticmethod
    def _translate_asset(data):
        return {
            'entities': [],
            'links': []
        }

    @staticmethod
    def _translate_folder(data):
        return {
            'entities': [],
            'links': []
        }


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_list_workflows(stderr, stdout):
    asset_service = MockAssetsService()
    asset_service.add_folder("/", "myfolder")
    asset_service.add_asset("/myfolder", "myasset.jpg")
    http_service = MockAssetsHttpService(asset_service)

    with HTTMock(http_service):
        server = Server('localhost')
        api = acmd.assets.AssetsApi(server)

        status, data = api.find("/")

        eq_(OK, status)
        eq_([], data)


def test_list_workflows2():
    pass
