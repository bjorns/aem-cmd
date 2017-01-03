# coding: utf-8
import json
from StringIO import StringIO

from httmock import urlmatch, HTTMock
from mock import patch
from nose.tools import eq_

import acmd.api.assets
from acmd import Server, OK

ROOT_DATA = {}
PROJECT_DATA = {}


class MockAssetsService(object):
    def __init__(self):
        pass

    def get(self, path):
        if path == "/":
            return ROOT_DATA
        else:
            return PROJECT_DATA


class MockAssetsHttpService(object):
    def __init__(self):
        self.service = MockAssetsService()
        self.request_log = []

    @urlmatch(netloc='localhost:4502')
    def __call__(self, url, request):
        self.request_log.append(request)
        if request.method == 'GET':
            return json.dumps(self.service.get("/"))
        else:
            raise Exception("Not implemented")


def test_something():
    server = Server("local")
    api = acmd.api.assets.AssetsApi(server)
    eq_(3, 3)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_list_workflows(stderr, stdout):
    service = MockAssetsHttpService()

    with HTTMock(service):
        server = Server('localhost')
        api = acmd.api.assets.AssetsApi(server)

        status, data = api.find("/")

        eq_(OK, status)
        eq_({}, data)
