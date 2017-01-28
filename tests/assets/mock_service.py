# coding: utf-8
import json

from httmock import urlmatch

import acmd.assets
import acmd.jcr.path
from acmd.strings import remove_suffix, remove_prefix

from tests.test_utils.logging import test_log


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
            properties={}
        )
        test_log("Creating asset {}".format(path))
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
        test_log("Creating folder {}".format(path))
        self.repo[path] = folder

    def get(self, path):
        test_log("Getting asset {} from {}".format(path, self.repo))
        return self.repo[path]


class MockAssetsHttpService(object):
    def __init__(self, service=None):
        self.service = MockAssetsService() if service is None else service
        self.request_log = []

    @urlmatch(netloc='localhost:4502')
    def __call__(self, url, request):
        self.request_log.append(request)
        if request.method == 'GET':
            service_path = self._get_api_path(url.path)
            data = self.service.get(service_path)
            return json.dumps(self._translate(data))
        if request.method == 'PUT':
            return json.dumps({})
        else:
            raise Exception("Method {} is not implemented".format(request.method))

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
            'links': [],
            'properties': data['properties']
        }

    @staticmethod
    def _translate_folder(data):
        return {
            'entities': [],
            'links': []
        }
