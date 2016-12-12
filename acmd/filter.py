# coding: utf-8
import json
import os

from acmd import log, error

class FileFilter(object):
    def __init__(self, filter_path):
        with open(filter_path, 'r') as stream:
            self.data = json.load(stream)

    def accept(self, filename):
        reject_obj = self.data.get('reject')
        accept_obj = self.data.get('accept', dict())

        ret = True

        if accept_obj:
            ret = ret and matches(accept_obj, filename)
        if reject_obj:
            ret = ret and not matches(reject_obj, filename)
        return ret


def matches(filter_obj, filepath):
    assert filter_obj is not None
    for filetype in filter_obj.get('filetypes', []):
        if filepath.endswith(filetype):
            return True
    for path in filter_obj.get('paths', []):
        try:
            if path in filepath:
                return True
        except UnicodeDecodeError:
            error(u"Failed to decode {}".format(path))
    for item in filter_obj.get('filenames', []):
        try:
            if item in os.path.basename(filepath):
                return True
        except UnicodeDecodeError:
            error(u"Failed to decode {}".format(path))
    return False
