# coding: utf-8
import json
import time

import requests

import acmd.jcr.path
from acmd import OK, SERVER_ERROR
from acmd import log, error

""" https://author-lbrands-assets-prod.adobecqms.net/api/assets/pink/INTIMATES_DESIGN/BRA/_BRA_SKETCHES/_JOCKTAG.ai.json
"""
API_ROOT = "/api/assets"


class AssetsApi(object):
    def __init__(self, server):
        self.server = server

    def get(self, path):
        """ Fetching asset info """
        req_path = "{root}{path}.json".format(root=API_ROOT, path=path)
        url = self.server.url(req_path)

        resp = requests.get(url, auth=self.server.auth)

        if resp.status_code != 200:
            return SERVER_ERROR, None

        data = resp.json()
        return OK, data

    def list(self, path):
        log("Fetching asset list for {}".format(path))
        req_path = "{root}{path}.json".format(root=API_ROOT, path=path)
        url = self.server.url(req_path)

        status, data = self.fetch_json(url)
        if status != OK:
            return SERVER_ERROR, None

        _add_path(data, path)

        next_url = _get_next_url(data)
        while next_url is not None:
            status, next_data = self.fetch_json(next_url)
            if status != OK:
                error("Failed to fetch next listing {}".format(next_url))
                next_url = None
            else:
                _add_path(next_data, path)
                data['entities'].extend(next_data['entities'])
                next_url = _get_next_url(next_data)
        return OK, data

    def fetch_json(self, url):
        log("Fetching url {}".format(url))
        resp = requests.get(url, auth=self.server.auth)

        if resp.status_code != 200:
            return SERVER_ERROR, None

        data = resp.json()
        return OK, data

    def find(self, path):
        status, root = self.list(path)
        if status != OK:
            error("Failed to find in {}".format(path))
            return SERVER_ERROR, None

        assets = _filter_assets(root['entities'])
        folder_queue = _filter_folders(root['entities'])

        while len(folder_queue) > 0:
            entity = folder_queue.pop()
            path = acmd.jcr.path.join(entity['properties']['path'], entity['properties']['name'])
            status, data = self.list(path)
            if status != OK:
                error("Failed to list contents of {}".format(path))
            else:
                for entity in data.get('entities', list()):
                    if _is_folder(entity):
                        folder_queue.insert(0, entity)
                    elif _is_asset(entity):
                        assets.append(entity)

        return OK, assets

    def touch(self, path):
        """ Trigger any update asset workflows for asset

            PUT /api/assets/myfolder/myAsset.png -H"Content-Type: application/json" \
                -d '{"class":"asset", "properties":{"dc:title":"My Asset"}}'
        """
        props = {'metadata/acmd_timestamp': str(time.time())}
        data = {
            'class': 'asset',
            'properties': props
        }
        req_path = API_ROOT + path
        url = self.server.url(req_path)
        log("Touching {}".format(url))

        r = requests.put(url, auth=self.server.auth, json=data)
        if r.status_code != 200:
            error("{} Failed to touch asset {}: {}".format(r.status_code, path, r.content))
            return SERVER_ERROR, None
        else:
            return OK, r.json()


def _add_path(data, path):
    for entity in data.get('entities', list()):
        entity['properties']['path'] = path


def _get_next_url(folder_listing):
    for link in folder_listing['links']:
        if link['rel'][0] == 'next':
            return link['href']
    return None


def _filter_assets(entities):
    return [x for x in entities if _is_asset(x)]


def _is_asset(entity):
    return entity['class'][0] == 'assets/asset'


def _filter_folders(entities):
    return [x for x in entities if _is_folder(x)]


def _is_folder(entity):
    mimetype = entity['class'][0]
    return mimetype == u'assets/folder'
