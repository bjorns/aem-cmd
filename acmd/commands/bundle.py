# coding: utf-8
import sys
import requests

from acmd.commands.registry import register_command

def get_bundle_list(server):
    url = server.url('/system/console/bundles.json')
    r = requests.get(url, auth=(server.username, server.password))
    if r.status_code != 200:
        raise Exception("Failed to get " + url)
    response = r.json()
    bundles = response['data']
    return bundles

def list_bundles(server):
    bundles = get_bundle_list(server)
    for bundle in bundles:
        print("{bundle}\t{version}\t{status}".format(
            bundle=bundle['symbolicName'],
            version=bundle['version'],
            status=bundle['state']))

def get_action(argv):
    if len(argv) < 2:
        return 'list'
    else:
        return argv[1]

class BundleCommand(object):
    def __init__(self):
        self.name = 'bundle'

    def execute(self, server, argv):
        action = get_action(argv)
        if action == 'list':
            list_bundles(server)
        else:
            sys.stderr.write('error: Unknown bundle action {a}\n'.format(a=action))
            sys.exit(-1)

cmd = BundleCommand()
register_command(cmd)
