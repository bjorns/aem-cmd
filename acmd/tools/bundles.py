# coding: utf-8
import sys
import optparse
import json

from acmd.http_util import get_json, post_form
from acmd.tool import tool

parser = optparse.OptionParser("acmd bundle [options] [list|start|stop] [<bundle>]")
parser.add_option("-v", "--verbose",
                  action="store_const", const=True, dest="verbose",
                  help="report verbose data when supported")


@tool('bundles')
class BundlesTool(object):
    def __init__(self):
        pass

    def execute(self, server, argv):
        (options, args) = parser.parse_args(argv)

        action = get_action(args)
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
    response = get_json(server, '/system/console/bundles.json')
    bundles = response['data']
    return bundles


def list_bundles(server, options):
    bundles = get_bundle_list(server)
    for bundle in bundles:
        if options.verbose:
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
    if options.verbose:
        sys.stdout.write(json.dumps(resp, indent=4) + "\n")


def start_bundle(server, bundlename, options):
    """ curl -u admin:admin http://localhost:4505/system/console/bundles/org.apache.sling.scripting.jsp
        -F action=start."""
    form_data = {'action': 'start'}
    path = '/system/console/bundles/{bundle}'.format(bundle=bundlename)
    resp = post_form(server, path, form_data)
    if options.verbose:
        sys.stdout.write(json.dumps(resp, indent=4) + "\n")


def get_action(argv):
    if len(argv) < 2:
        return 'list'
    else:
        return argv[1]


def get_argument(argv):
    if len(argv) < 3:
        return None
    else:
        return argv[2]
