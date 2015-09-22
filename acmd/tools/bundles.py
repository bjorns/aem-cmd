# coding: utf-8
import sys
import optparse
import json

import requests

from acmd import tool, log, error
from acmd.tools import get_command, get_argument

parser = optparse.OptionParser("acmd bundle [options] [list|start|stop] [<bundle>]")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")
parser.add_option("-c", "--compact",
                  action="store_const", const=True, dest="compact",
                  help="output only package name")


@tool('bundles', ['list', 'start', 'stop'])
class BundlesTool(object):
    def execute(self, server, argv):
        (options, args) = parser.parse_args(argv)

        action = get_command(args, 'list')
        actionarg = get_argument(args)
        if action == 'list' or action == 'ls':
            return list_bundles(server, options)
        elif action == 'start':
            return start_bundle(server, actionarg, options)
        elif action == 'stop':
            return stop_bundle(server, actionarg, options)
        else:
            sys.stderr.write('error: Unknown {t} action {a}\n'.format(t=self.name, a=action))
            return -2


def get_bundle_list(server):
    url = server.url('/system/console/bundles.json')

    log("GETting service {}".format(url))
    response = requests.get(url, auth=server.auth)

    if response.status_code != 200:
        error("Failed to list bundles: {}".format(response.status_code))
        return []
    bundles = response.json()['data']
    return bundles


def list_bundles(server, options):
    bundles = get_bundle_list(server)
    for bundle in bundles:
        if options.compact:
            sys.stdout.write("{bundle}\n".format(bundle=bundle['symbolicName']))
        elif options.raw:
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
    url = server.url('/system/console/bundles/{bundle}'.format(bundle=bundlename))
    log("POSTing to service {}".format(url))
    resp = requests.post(url, auth=(server.username, server.password), data=form_data)
    if resp.status_code != 200:
        error("Failed to stop bundle {bundle}: {status}".format(bundle=bundlename, status=resp.status_code))
        return -1
    elif options.raw:
        sys.stdout.write("{}\n".format(resp.content))


def start_bundle(server, bundlename, options):
    """ curl -u admin:admin http://localhost:4505/system/console/bundles/org.apache.sling.scripting.jsp
        -F action=start."""
    form_data = {'action': 'start'}
    url = server.url('/system/console/bundles/{bundle}'.format(bundle=bundlename))
    log("POSTing to service {}".format(url))
    resp = requests.post(url, auth=(server.username, server.password), data=form_data)
    if options.raw:
        sys.stdout.write("{}\n".format(resp.content))
