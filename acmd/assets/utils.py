# coding: utf-8
import os
import re

from acmd.jcr.path import join


ROOT_IMPORT_DIR = "/tmp/acmd_assets_ingest"


class AssetException(Exception):
    pass


def get_dam_path(filepath, local_import_root, dam_import_root):
    local_dir = os.path.dirname(filepath)
    if dam_import_root is None:
        dam_import_root = join('/', os.path.basename(local_import_root))
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


def filter_unwanted(filename):
    """ Returns true for hidden or unwanted files """
    return filename.startswith(".")


def status_ok(status_code):
    """ Returns true if http status code is considered success """
    return status_code == 200 or status_code == 201
