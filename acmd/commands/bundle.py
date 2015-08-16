# coding: utf-8
import sys
import optparse
import requests

from acmd.commands.registry import register_command
from acmd.http_util import get_json, post_form

parser = optparse.OptionParser("acmd [options] <command> <args>")
parser.add_option("-v", "--verbose", dest="verbose",
                  help="report verbose data when supported", metavar="bool")


def get_bundle_list(server):
    response = get_json(server, '/system/console/bundles.json')
    bundles = response['data']
    return bundles

def list_bundles(server):
    bundles = get_bundle_list(server)
    for bundle in bundles:
        sys.stdout.write("{bundle}\t{version}\t{status}\n".format(
            bundle=bundle['symbolicName'],
            version=bundle['version'],
            status=bundle['state']))

def stop_bundle(server, bundlename):
    """ curl -u admin:admin http://localhost:4505/system/console/bundles/org.apache.sling.scripting.jsp
        -F action=stop."""
    form_data = {'action': 'stop'}
    path = '/system/console/bundles/{bundle}'.format(bundle=bundlename)
    return post_form(server, path, form_data)


def start_bundle(server, bundlename):
    """ curl -u admin:admin http://localhost:4505/system/console/bundles/org.apache.sling.scripting.jsp
        -F action=start."""
    form_data = {'action': 'start'}
    path = '/system/console/bundles/{bundle}'.format(bundle=bundlename)
    return post_form(server, path, form_data)


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


class BundleCommand(object):
    def __init__(self):
        self.name = 'bundle'

    def execute(self, server, argv):
        (options, args) = parser.parse_args(argv)

        action = get_action(args)
        actionarg = get_argument(args)
        if action == 'list':
            list_bundles(server)
        elif action == 'start':
            start_bundle(server, actionarg)
        elif action == 'stop':
            stop_bundle(server, actionarg)
        else:
            sys.stderr.write('error: Unknown bundle action {a}\n'.format(a=action))
            sys.exit(-1)


cmd = BundleCommand()
register_command(cmd)
