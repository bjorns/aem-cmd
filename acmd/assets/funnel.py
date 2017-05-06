# coding: utf-8
import os
import sys

from acmd import SERVER_ERROR, OK, error, log

from .utils import filter_unwanted, get_dam_path
from .utils import AssetException
from acmd.assets.api import AssetsApi


class AssetImportFunnel(object):
    def __init__(self, server, dry_run=False, destination_root=None):
        self.server = server
        self.dry_run = dry_run
        self.destination_root = destination_root
        self.current_file = 0
        self.created_paths = set([])
        self.api = AssetsApi(self.server)

    def import_path(self, path):
        """ Import generic file system path, could be file or dir """
        if self.dry_run:
            log("Dry running import")

        if os.path.isdir(path):
            return self.import_directory(path)
        else:
            import_root = os.path.dirname(path)
            if self.destination_root is not None:
                import_root = self.destination_root
            return self.import_file(import_root, path)

    def import_directory(self, import_dir):
        """ Import directory recursively """
        assert os.path.isdir(import_dir)

        if import_dir.endswith("/"):
            import_dir = import_dir[:-1]

        status = OK
        for subdir, dirs, files in os.walk(import_dir):
            # _create_dir(server, subdir)
            for filename in files:
                filepath = os.path.join(subdir, filename)
                try:
                    if filter_unwanted(filename):
                        log("Skipping {path}".format(path=filepath))
                        continue
                    self.import_file(import_dir, filepath)
                except AssetException as e:
                    error("Failed to import {}: {}".format(filepath, e.message))
                    status = SERVER_ERROR
                self.current_file += 1
        return status

    def import_file(self, local_import_root, filepath):
        """ Import single file """
        assert os.path.isfile(filepath)

        dam_path = get_dam_path(filepath, local_import_root, self.destination_root)

        log("Uplading {} to {}".format(filepath, dam_path))

        if dam_path not in self.created_paths:
            self.created_paths.add(dam_path)
            if not self.dry_run:
                self.api.create_folder(dam_path)
        else:
            log("Skipping creating dam path {}".format(dam_path))

        status = OK
        if not self.dry_run:
            status = self.api.create_asset(filepath, dam_path)

        if status == OK:
            sys.stdout.write("{local} -> {dam}\n".format(local=filepath, dam=dam_path))
            sys.stdout.flush()
        return status
