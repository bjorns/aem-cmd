# coding: utf-8
import sys
import optparse
import json

from acmd.tool_repo import tool
from acmd.http_util import get_json, post_form
from acmd.tools.tool_utils import get_command, get_argument

parser = optparse.OptionParser("acmd bundle [options] [list|start|stop] [<bundle>]")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")


@tool('bundles')
class BundlesTool(object):
    def execute(self, server, argv):
        (options, args) = parser.parse_args(argv)

        action = get_command(args, 'list')
        actionarg = get_argument(args)
        if action == 'list':
            list_bundles(server, options)
        elif action == 'start':
            start_bundle(server, actionarg, options)
        elif action == 'stop':
            stop_bundle(server, actionarg, options)
        else:
            sys.stderr.write('error: Unknown {t} action {a}\n'.format(t=self.name, a=action))
            sys.exit(-1)


def get_bundle_list(server):
    status, response = get_json(server, '/system/console/bundles.json')
    if status != 200:
        sys.stderr.write("error: Failed to list bundles: {}".format(status))
        sys.exit(-1)
    bundles = response['data']
    return bundles


def list_bundles(server, options):
    bundles = get_bundle_list(server)
    for bundle in bundles:
        if options.raw:
            sys.stdout.write(json.dumps(bundle, indent=4) + "\n")
        else:
            sys.stdout.write("{bundle}\t{version}\t{status}\n".format(
                bundle=bundle['symbolicName'],
                version=bundle['version'],
                status=bundle['state']))


def stop_bundle(server, bundlename, options):
    """ curl -u admin:admin http://localhost:4505/system/console/bundles/org.apache.sling.scripting.jsp
        -F action=stop."""
    form_data = {'action': 'stop'}
    path = '/system/console/bundles/{bundle}'.format(bundle=bundlename)
    resp = post_form(server, path, form_data)
    if options.raw:
        sys.stdout.write(json.dumps(resp, indent=4) + "\n")


def start_bundle(server, bundlename, options):
    """ curl -u admin:admin http://localhost:4505/system/console/bundles/org.apache.sling.scripting.jsp
        -F action=start."""
    form_data = {'action': 'start'}
    path = '/system/console/bundles/{bundle}'.format(bundle=bundlename)
    resp = post_form(server, path, form_data)
    if options.raw:
        sys.stdout.write(json.dumps(resp, indent=4) + "\n")
