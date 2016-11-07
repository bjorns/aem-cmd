# coding: utf-8

import yaml


class FileFilter(object):
    def __init__(self, filter_path):
        with open(filter_path, 'r') as stream:
            self.data = yaml.load(stream)

    def accept(self, filename):
        reject_obj = self.data.get('reject')
        accept_obj = self.data.get('accept', dict())

        if reject_obj is None:
            return matches(accept_obj, filename)
        else:
            return not matches(reject_obj, filename)


def matches(filter_obj, filename):
    for filetype in filter_obj.get('filetypes', []):
        if filename.endswith(filetype):
            return True
    for path in filter_obj.get('paths', []):
        if path in filename:
            return True
    return False
