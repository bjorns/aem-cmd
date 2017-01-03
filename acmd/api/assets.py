# coding: utf-8
import requests

from acmd import OK, SERVER_ERROR
from acmd import log, error
import acmd.jcr.path

""" https://author-lbrands-assets-prod.adobecqms.net/api/assets/pink/INTIMATES_DESIGN/BRA/_BRA_SKETCHES/_JOCKTAG.ai.json
"""
API_ROOT = "/api/assets"


class AssetsApi(object):
    def __init__(self, server):
        self.server = server

    def list(self, path):
        log("Fetching asset list for {}".format(path))
        req_path = "{root}{path}.json".format(root=API_ROOT, path=path)
        url = self.server.url(req_path)

        resp = requests.get(url, auth=self.server.auth)

        if resp.status_code != 200:
            return SERVER_ERROR, None

        data = resp.json()
        for entity in data.get('entities', list()):
            entity['properties']['path'] = path
        return OK, data

    def find(self, path):
        status, root = self.list(path)
        if status != OK:
            error("Failed to find in {}".format(path))
            return SERVER_ERROR, None

        assets = _filter_assets(root['entities'])
        log("Assets is {}".format(assets))
        folder_queue = _filter_folders(root['entities'])
        log("Folders are {}".format(assets))

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


def _filter_assets(entities):
    return [x for x in entities if _is_asset(x)]


def _is_asset(entity):
    return entity['class'][0] == 'assets/asset'


def _filter_folders(entities):
    return [x for x in entities if _is_folder(x)]


def _is_folder(entity):
    mimetype = entity['class'][0]
    return mimetype == u'assets/folder'
