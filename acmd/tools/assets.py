# coding: utf-8
import sys
import optparse

from acmd import USER_ERROR, SERVER_ERROR
from acmd import tool, error
from acmd.tools.tool_utils import get_argument, get_command
from acmd.tools.asset_import import *

from acmd.assets import AssetsApi

parser = optparse.OptionParser("acmd assets <import|touch> [options] <file>")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")
parser.add_option("-D", "--dry-run",
                  action="store_const", const=True, dest="dry_run",
                  help="Do not change repository")
parser.add_option("-d", "--destination", dest="destination_root",
                  help="The root directory to import to")


@tool('assets')
class AssetsTool(object):
    """ Manage AEM DAM assets """

    def __init__(self):
        self.created_paths = set([])
        self.current_file = 1
        self.api = None

    def execute(self, server, argv):
        self.api = AssetsApi(server)

        options, args = parser.parse_args(argv)

        action = get_command(args)
        actionarg = get_argument(args)

        if action == 'import':
            return self.import_path(server, options, actionarg)
        elif action == 'touch':
            if len(args) >= 3:
                self._touch(actionarg)
            else:
                for line in sys.stdin:
                    self._touch(line.strip())
            return OK
        elif action == 'list' or action == 'ls':
            status, data = self.api.list(actionarg)
            if status != OK:
                return status
            for item in data['entities']:
                print item['properties']['name']
        elif action == 'find':
            status, data = self.api.find(actionarg)
            if status != OK:
                return status
            for item in data:
                props = item['properties']
                path = acmd.jcr.path.join(props['path'], props['name'])
                sys.stdout.write("{}\n".format(path))
        else:
            error("Unknown action {}".format(action))
            return USER_ERROR

    def _touch(self, path):
        status, _ = self.api.touch(path)
        if status != OK:
            error("Failed to touch {}".format(path))
        sys.stdout.write("{}\n".format(path))

    def import_path(self, server, options, path):
        """ Import generic file system path, could be file or dir """
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

        status = OK
        for subdir, dirs, files in os.walk(import_dir):
            # _create_dir(server, subdir)
            for filename in files:
                filepath = os.path.join(subdir, filename)
                try:
                    if filter_unwanted(filename):
                        log("Skipping {path}".format(path=filepath))
                        continue
                    self.import_file(server, options, import_dir, filepath)
                except AssetException as e:
                    error("Failed to import {}: {}".format(filepath, e.message))
                    status = SERVER_ERROR
                self.current_file += 1
        return status

    def import_file(self, server, options, local_import_root, filepath):
        """ Import single file """
        assert os.path.isfile(filepath)

        dam_path = get_dam_path(filepath, local_import_root, options.destination_root)

        log("Uplading {} to {}".format(filepath, dam_path))

        if dam_path not in self.created_paths:
            create_dir(server, dam_path, options.dry_run)
            self.created_paths.add(dam_path)
        else:
            log("Skipping creating dam path {}".format(dam_path))

        post_file(server, filepath, dam_path, options.dry_run)
        sys.stdout.write("{local} -> {dam}\n".format(local=filepath, dam=dam_path))
        sys.stdout.flush()
        return OK
