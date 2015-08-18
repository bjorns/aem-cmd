# coding: utf-8
import sys
import optparse
import requests
import json
from xml.etree import ElementTree

from acmd.commands.registry import register_command
from acmd.http_util import get_json, post_form

parser = optparse.OptionParser("acmd packages [options] [upload] [<zip>|<package>]")
parser.add_option("-v", "--verbose",
                action="store_const", const=True, dest="verbose",
                help="report verbose data when supported")


class PackagesCommand(object):
    def __init__(self):
        self.name = 'packages'

    def execute(self, server, argv):
        (options, args) = parser.parse_args(argv)

        action = get_action(args)
        actionarg = get_argument(args)
        if action == 'list':
            list_packages(server, options)
        elif action == 'upload':
            upload_package(server, options)
        else:
            sys.stderr.write('error: Unknown bundle action {a}\n'.format(a=action))
            sys.exit(-1)


class PackagesResponse(object):
    """ Iterable for xml packages list. """

    def __init__(self, tree):
        pass


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

def list_packages(server, options):
    url = server.url('/crx/packmgr/service.jsp')
    form_data = {'cmd': (None, 'ls') }
    resp = requests.post(url, auth=(server.username, server.password), files=form_data)
    if resp.status_code != 200:
        raise Exception("Failed to get " + url)

    tree = ElementTree.fromstring(resp.content)
    packages = parse_packages(tree)
    for pkg in packages:
        if options.verbose:
            sys.stdout.write("{s}\n".format(s=json.dumps(pkg, indent=4)))
        else:
            sys.stdout.write("{g}\t{pkg}\t{v}\n".format(g=pkg['group'], pkg=pkg['name'], v=pkg['version']))



def parse_packages(tree):
    pkgElems = tree.find('response').find('data').find('packages').findall('package')
    packages = [parse_package(elem) for elem in pkgElems]
    return packages

def parse_package(elem):
    ret = dict()
    for sub in elem.getchildren():
        ret[sub.tag] = sub.text
    return ret

def upload_package(server, options):
    """curl -u admin:admin -F file=@"name of zip file" -F name="name of package"
            -F force=true -F install=false http://localhost:4505/crx/packmgr/service.jsp"""
    pass


cmd = PackagesCommand()
register_command(cmd)
