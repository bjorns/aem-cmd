# coding: utf-8
import mimetypes
import os
import time
import json
import requests

from acmd.jcr.path import join
from acmd import OK, UNCHANGED, SERVER_ERROR
from acmd import log, error
from acmd.util.strings import remove_prefix
from acmd.assets.utils import status_ok, AssetException

""" https://author-lbrands-assets-prod.adobecqms.net/api/assets/pink/INTIMATES_DESIGN/BRA/_BRA_SKETCHES/_JOCKTAG.ai.json
"""
API_ROOT = "/api/assets"


class AssetsApi(object):
    def __init__(self, server):
        self.server = server

    def get(self, path):
        """ Fetch asset info """
        req_path = "{root}{path}.json".format(root=API_ROOT, path=path)
        url = self.server.url(req_path)
        resp = requests.get(url, auth=self.server.auth)
        if resp.status_code != 200:
            return SERVER_ERROR, None

        data = json.loads(resp.content)
        return OK, data

    def create_asset(self, src_file, dst_path):
        """ Upload <src_file> to folder <dst_path> in the dam
          
            src_file: an absolute or relative path on the local filesystem
            dst_path: an absolute path within the DAM. 
                Note: this does not include the '/content/dam' prefix of the JCR.
        """
        assert os.path.isfile(src_file)
        if dst_path.startswith('/content/dam'):
            return AssetException("Destination path is in DAM and should not include /content/dam")

        filename = os.path.basename(src_file)
        f = open(src_file, 'rb')
        mime, enc = mimetypes.guess_type(src_file)
        log("Uploading {} as {}, {}".format(f, mime, enc))

        dam_path = "/api/assets{path}/{filename}".format(path=dst_path, filename=filename)
        url = self.server.url(dam_path)
        log("POSTing to {}".format(url))
        form_data = dict(
            file=(filename, f, mime, dict()),
        )

        resp = requests.post(url, auth=self.server.auth, files=form_data)
        if resp.status_code == 409:
            log("Asset {} already exists".format(url))
            return UNCHANGED
        if not status_ok(resp.status_code):
            raise AssetException("Failed to upload file {}\n{}".format(src_file, resp.content))
        return OK

    def create_folder(self, path):
        """ Create folder in the DAM
            
            POST /api/assets/myFolder -H"Content-Type: application/json" 
                -d '{"class":"assetFolder","properties":{"title":"My Folder"}}'

        """
        log("Creating DAM folder {}".format(path))
        if not path.startswith('/'):
            raise AssetException("Can only create asset folder with absolute path")
        if path.startswith('/content/dam'):
            raise AssetException("Do not create folders with jcr path, please remove /content/dam-prefix.")

        headers = {'Content-Type': 'application/json'}
        json_data = {'class': 'assetFolder'}
        url = self.server.url("/api/assets{path}".format(path=path))
        log("POSTing to {}".format(url))
        resp = requests.post(url, auth=self.server.auth, json=json_data, headers=headers)

        if resp.status_code == 409:
            log("Folder {} already exists".format(url))
            return UNCHANGED
        if not status_ok(resp.status_code):
            raise AssetException("Failed to create directory {}\n{}".format(url, resp.content))
        return OK

    def _list_assets(self, path):
        """ List assets under path
         
            :return (<status>, <list>)
            <status>: <OK|USER_ERROR|SERVER_ERROR>
            <list> [{name: <name>, title: <title>}...]
        """

        log("Fetching asset list for {}".format(path))
        req_path = "{root}{path}.json".format(root=API_ROOT, path=path)
        url = self.server.url(req_path)

        status, data = self._fetch_json(url)
        if status != OK:
            return SERVER_ERROR, None

        _add_path(data, path)

        next_url = _get_next_url(data)
        while next_url is not None:
            status, next_data = self._fetch_json(next_url)
            if status != OK:
                error("Failed to fetch next listing {}".format(next_url))
                next_url = None
            else:
                _add_path(next_data, path)
                data['entities'].extend(next_data['entities'])
                next_url = _get_next_url(next_data)
        return OK, data

    def _fetch_json(self, url):
        log("Fetching url {}".format(url))
        resp = requests.get(url, auth=self.server.auth)

        if resp.status_code != 200:
            return SERVER_ERROR, None

        data = json.loads(resp.content)
        return OK, data

    def find(self, path):
        if path.startswith("/content/dam"):
            path = remove_prefix("/content/dam", path)

        status, root = self._list_assets(path)
        if status != OK:
            error("Failed to find in {}".format(path))
            return SERVER_ERROR, None

        assets = _filter_assets(root['entities'])
        folder_queue = _filter_folders(root['entities'])

        while len(folder_queue) > 0:
            entity = folder_queue.pop()
            path = join(entity['properties']['path'], entity['properties']['name'])
            status, data = self._list_assets(path)
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

    def setprops(self, path, properties):
        """
        Update metadata properties:
        path: /hosts/arnold.png
        properties: {'dc:title': 'Arnold'}

        PUT /api/assets/hosts/arnold.jpg -H"Content-Type: application/json" -d '{"class":"asset", \
            "properties":{"dc:title":"Arnold"}}'
        """
        data = {'class': 'asset', 'properties': properties}
        url = self.server.url("/api/assets{}".format(path))
        r = requests.put(url, auth=self.server.auth, json=data)
        if r.status_code != 200:
            error("{} Failed to touch asset {}: {}".format(r.status_code, path, r.content))
            return SERVER_ERROR, None
        else:
            return OK, json.loads(r.content)


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
