# coding: utf-8
import sys
import optparse

from acmd import OK, USER_ERROR, tool, error, log
from acmd.tools.tool_utils import get_argument, get_command
from acmd.workflows import WorkflowsApi

import acmd.jcr.path
from acmd.assets import AssetsApi, AssetsImportFunnel

parser = optparse.OptionParser("acmd assets <import|touch> [options] <file>")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")
parser.add_option("-D", "--dry-run",
                  action="store_const", const=True, dest="dry_run",
                  help="Do not change repository")
parser.add_option("-d", "--destination", dest="destination_root",
                  help="The root directory to import to")
parser.add_option("-m", "--model", dest="model", default="dam/update_asset",
                  help="Update assets model to use, defaults to dam/update_asset")


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
            funnel = AssetsImportFunnel(server, dry_run=options.dry_run, destination_root=options.destination_root)
            return funnel.import_path(actionarg)
        elif action == 'touch':
            api = WorkflowsApi(server)
            if len(args) >= 3:
                self._touch(api, actionarg, options.model)
            else:
                for line in sys.stdin:
                    self._touch(api, line.strip(), options.model)
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

    def _touch(self, api, path, model):
        path = "/content/dam" + path + "/jcr:content/renditions/original"
        log("Triggering workflow {} on {}".format(model, path))

        api.start_workflow(model, path)
        print path
