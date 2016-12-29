# coding: utf-8
import mimetypes
import os
import re

import requests

from acmd import OK
from acmd import log
import acmd.jcr


ROOT_IMPORT_DIR = "/tmp/acmd_assets_ingest"


class AssetException(Exception):
    pass


def get_dam_path(filepath, local_import_root, dam_import_root):
    local_dir = os.path.dirname(filepath)
    if dam_import_root is None:
        dam_import_root = acmd.jcr.path.join('/content/dam', os.path.basename(local_import_root))
    dam_path = create_dam_path(local_dir, local_import_root, dam_import_root)
    return clean_path(dam_path)


def create_dam_path(local_path, local_import_root, dam_import_root):
    """ Returns <ok>, <path> """
    ret = local_path.replace(local_import_root, dam_import_root)
    ret = ret.replace("\\", "/")
    return ret


def clean_path(path):
    """ Replace spaces in target path """
    ret = path.replace(' ', '_')
    pattern = re.compile("[a-zA-Z0-9_/-]+")
    if pattern.match(ret) is None:
        raise AssetException("File path {} contains unallowed characters".format(path))
    return ret


def create_dir(server, path, dry_run):
    """ Create file in the DAM
        e.g. curl -s -u admin:admin -X POST -F "jcr:primaryType=sling:OrderedFolder" $HOST$dampath > /dev/null
    """
    if dry_run:
        log("SKipping creating folder, dry run")
        return

    form_data = {'jcr:primaryType': 'sling:OrderedFolder'}
    url = server.url(path)
    log("POSTing to {}".format(url))
    resp = requests.post(url, auth=server.auth, data=form_data)
    if not _ok(resp.status_code):
        raise AssetException("Failed to create directory {}\n{}".format(url, resp.content))


def post_file(server, filepath, dst_path, dry_run):
    """ POST single file to DAM
        curl -v -u admin:admin -X POST -i -F "file=@\"$FILENAME\"" $HOST$dampath.createasset.html &> $tempfile
    """
    assert os.path.isfile(filepath)

    if dry_run:
        return OK

    filename = os.path.basename(filepath)
    f = open(filepath, 'rb')
    mime, enc = mimetypes.guess_type(filepath)
    log("Uploading {} as {}, {}".format(f, mime, enc))
    form_data = dict(
        file=(filename, f, mime, dict()),
        fileName=clean_path(filename)
    )

    url = server.url("{path}.createasset.html".format(path=dst_path, filename=os.path.basename(filepath)))
    log("POSTing to {}".format(url))
    resp = requests.post(url, auth=server.auth, files=form_data)
    if not _ok(resp.status_code):
        raise AssetException("Failed to upload file {}\n{}".format(filepath, resp.content))
    return OK


def filter_unwanted(filename):
    """ Returns true for hidden or unwanted files """
    return filename.startswith(".")


def _ok(status_code):
    """ Returns true if http status code is considered success """
    return status_code == 200 or status_code == 201
