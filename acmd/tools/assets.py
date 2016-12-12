# coding: utf-8
import optparse

import sys
import time

from acmd import USER_ERROR, SERVER_ERROR
from acmd import tool, error
from acmd.tools.tool_utils import get_argument, get_command
from acmd.tools.asset_import import *
from acmd.filter import FileFilter

parser = optparse.OptionParser("acmd assets <import|touch> [options] <file>")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")
parser.add_option("-D", "--dry-run",
                  action="store_const", const=True, dest="dry_run",
                  help="Do not change repository")
parser.add_option("-d", "--destination", dest="destination_root",
                  help="The root directory to import to")
parser.add_option("-q", "--local-root", dest="local_root",
                  help="The local root directory to map to the destination root")
parser.add_option("-l", "--lock-dir", dest="lock_dir",
                  help="Directory to store information on uploaded files")
parser.add_option("-f", "--filter", dest="filter_file",
                  help="Read filtering config from json file")


@tool('assets')
class AssetsTool(object):
    """ Manage AEM DAM assets """

    def __init__(self):
        self.created_paths = set([])
        self.total_files = 1
        self.current_file = 1
        self.upload_registry = None
        self.file_filter = None

    def execute(self, server, argv):
        options, args = parser.parse_args(argv)

        action = get_command(args)
        actionarg = get_argument(args)

        if action == 'import':
            return self.import_path(server, options, actionarg)
        else:
            error("Unknown action {}".format(action))
            return USER_ERROR

    def import_path(self, server, options, path):
        """ Import generic file system path, could be file or dir """
        self.upload_registry = UploadRegistry(server, path, options.lock_dir)
        if options.filter_file:
            self.file_filter = FileFilter(options.filter_file)
        if options.dry_run:
            log("Dry running import")

        if os.path.isdir(path):
            return self.import_directory(server, options, path)
        else:
            import_root = os.path.dirname(path)
            if options.destination_root is not None:
                import_root = options.destination_root
            return self.import_file(server, options, import_root, path)

    def import_directory(self, server, options, import_dir):
        """ Import directory recursively """
        assert os.path.isdir(import_dir)

        if import_dir.endswith("/"):
            import_dir = import_dir[:-1]

        local_root = options.local_root if options.local_root else import_dir
        log("Local root set to {}".format(local_root))
        self.total_files = count_files(import_dir)
        log("Importing {n} files in {path}".format(n=self.total_files, path=import_dir))

        status = OK
        for subdir, dirs, files in os.walk(import_dir):
            # _create_dir(server, subdir)
            for filename in files:
                filepath = os.path.join(subdir, filename)
                try:
                    if filter_unwanted(filename):
                        log("Skipping {path}".format(path=filepath))
                        continue
                    self.import_file(server, options, local_root, filepath)
                except AssetException as e:
                    error("Failed to import {}: {}".format(filepath, e.message))
                    status = SERVER_ERROR
                self.current_file += 1
        return status

    def import_file(self, server, options, local_import_root, filepath):
        """ Import single file """
        assert os.path.isfile(filepath)
        t0 = time.time()

        if self.file_filter and not self.file_filter.accept(filepath):
            msg = "{ts}\t{i}/{n}\tFiltered {local}".format(ts=format_timestamp(time.time()),
                                                             i=self.current_file,
                                                             n=self.total_files,
                                                             local=filepath)
            log(msg)
            return OK

        if self.upload_registry.is_uploaded(filepath):
            msg = "{ts}\t{i}/{n}\tSkipping {local}\n".format(ts=format_timestamp(time.time()),
                                                             i=self.current_file,
                                                             n=self.total_files,
                                                             local=filepath)
            sys.stdout.write(msg)
            sys.stdout.flush()
            return OK

        dam_path = get_dam_path(filepath, local_import_root, options.destination_root)

        log("Uplading {} to {}".format(filepath, dam_path))

        if dam_path not in self.created_paths:
            create_dir(server, dam_path, options.dry_run)
            self.created_paths.add(dam_path)
        else:
            log("Skipping creating dam path {}".format(dam_path))

        post_file(server, filepath, dam_path, options.dry_run)
        t1 = time.time()
        benchmark = '{0:.3g}'.format(t1 - t0)
        sys.stdout.write("{ts}\t{i}/{n}\t{local} -> {dam}\t{benchmark}\n".format(ts=format_timestamp(t1),
                                                                                 i=self.current_file,
                                                                                 n=self.total_files,
                                                                                 local=filepath, dam=dam_path,
                                                                                 benchmark=benchmark))
        sys.stdout.flush()
        self.upload_registry.mark_uploaded(filepath, options.dry_run)
        return OK
