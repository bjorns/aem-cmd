# coding: utf-8
import datetime
import hashlib
import mimetypes
import os
import re

import requests

from acmd import OK
from acmd import log
from acmd.tools.utils import aem


TMP_ROOT = "/tmp" if os.name == 'posix' else 'C:\\tmp'
ROOT_IMPORT_DIR = os.path.join(TMP_ROOT, "acmd_assets_ingest")


class AssetException(Exception):
    pass


class UploadRegistry(object):
    def __init__(self, server, path, force_root=None):
        if force_root is not None:
            self.lock_dir = force_root
        else:
            self.lock_dir = os.path.join(ROOT_IMPORT_DIR, self._hash_job(server, path))
        log("Cache dir is {}".format(self.lock_dir))

    @staticmethod
    def _hash_job(server, path):
        """ Produce unique folder for upload based on path and server """
        return hashlib.sha1('{}:{}'.format(server.name, path)).hexdigest()[:8]

    def is_uploaded(self, filepath):
        lock_file = self._lock_file(filepath)
        log("Checking lock file {}".format(lock_file))
        return os.path.exists(lock_file)

    def _lock_file(self, filepath, os_name=os.name):
        """ Return the filepath to the lock file for a given file """
        if os_name == 'posix':
            if filepath.startswith('/'):
                filepath = filepath[1:]
            return os.path.join(self.lock_dir, filepath)
        else:
            if filepath[1] == ':':
                filepath = filepath[3:]
            return os.path.join(self.lock_dir, filepath)

    def mark_uploaded(self, filepath, dry_run=False):
        lock_file = self._lock_file(filepath, dry_run)
        self._touch(lock_file, dry_run)

    @staticmethod
    def _touch(filename, dry_run=False):
        """ Create empty file """
        par_dir = os.path.dirname(filename)
        if dry_run:
            log("Skipping creating dir {} because dry run".format(par_dir))
            return
        if not os.path.exists(par_dir):
            log("Creating directory {}".format(par_dir))
            os.makedirs(par_dir, mode=0755)
        log("Creating lock file {}".format(filename))
        open(filename, 'a').close()


def get_dam_path(filepath, local_import_root, dam_import_root):
    local_dir = os.path.dirname(filepath)
    if dam_import_root is None:
        dam_import_root = aem.path.join('/content/dam', os.path.basename(local_import_root))
    dam_path = create_dam_path(local_dir, local_import_root, dam_import_root)
    return dam_path


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


def format_timestamp(t):
    return datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')


def hash_job(server, path):
    """ Produce unique folder for upload based on path and server """
    return hashlib.sha1('{}:{}'.format(server.name, path)).hexdigest()[:8]


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
        fileName=filename
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


def count_files(dirpath):
    """ Return the number of files in directory """
    i = 0
    for subdir, dirs, files in os.walk(dirpath):
        for filename in files:
            if not filter_unwanted(filename):
                i += 1
    return i
