# coding: utf-8
import json

from httmock import urlmatch

import acmd.assets
import acmd.jcr.path

from acmd.util.strings import remove_suffix, remove_prefix

from test_utils.logging import test_log


class MockAssetsService(object):
    def __init__(self):
        self.repo = dict()
        self.repo['/'] = dict(
            type='assets/folder',
            name="/",
            path="/",
            parent=None,
            folders=[],
            assets=[]
        )

    def add_asset(self, parentpath, name):
        parent = self.repo[parentpath]
        path = acmd.jcr.path.join(parentpath, name)
        assert path not in self.repo

        asset = dict(
            type='assets/asset',
            name=name,
            parent=parent,
            path=path,
            properties=dict(),
            assets=[],
            folders=[],
        )
        test_log("Creating asset {}".format(path))
        self.repo[path] = asset
        parent['assets'].append(asset)

    def add_folder(self, parentpath, name):
        parent = self.repo[parentpath]
        path = acmd.jcr.path.join(parentpath, name)
        folder = dict(
            type='assets/folder',
            name=name,
            path=path,
            parent=parent,
            folders=[],
            assets=[]
        )
        parent['folders'].append(folder)
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
            return json.dumps(_translate(data))
        if request.method == 'PUT':
            return json.dumps({})
        else:
            raise Exception("Method {} is not implemented".format(request.method))

    @staticmethod
    def _get_api_path(path):
        return remove_suffix('.json', remove_prefix('/api/assets', path))


def _translate(data):
    if data['type'] == 'assets/asset':
        return _translate_resource(data)
    elif data['type'] == 'assets/folder':
        return _translate_resource(data)
    else:
        raise Exception()


def _translate_resource(resource):
    ret = {
        'entities': [_translate_entity(a) for a in resource['assets']],
        'links': [],
        "class": [
            ['type']
        ],
        'actions': [],
        'properties': {
            'name': resource['name'],
            'path': resource['path']
        }
    }
    for f in resource['folders']:
        ret['entities'].append(_translate_entity(f))
    return ret


def _translate_entity(entity):
    ret = {
        'links': [],
        "class": [
            entity['type']
        ],
        'properties': {
            'name': entity['name'],
            'path': entity['path']
        }
    }
    return ret
