# coding: utf-8
import sys
import optparse
import json
from xml.etree import ElementTree

import requests

from acmd import tool

parser = optparse.OptionParser("acmd packages [options] [list|upload] [<zip>|<package>]")
parser.add_option("-v", "--version",
                  dest="version", help="specify explicit version")
parser.add_option("-g", "--group",
                  dest="group", help="specify explicit group")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")


@tool('packages')
class PackagesTool(object):
    def execute(self, server, argv):
        (options, args) = parser.parse_args(argv)

        action = get_action(args)
        actionarg = get_argument(args)
        if action == 'list':
            list_packages(server, options)
        elif action == 'download':
            download_package(server, actionarg, options)
        elif action == 'upload':
            upload_package(server, options)
        else:
            sys.stderr.write('error: Unknown bundle action {a}\n'.format(a=action))
            sys.exit(-1)


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


def get_packages_list(server, options):
    url = server.url('/crx/packmgr/service.jsp')
    form_data = {'cmd': (None, 'ls')}
    resp = requests.post(url, auth=(server.username, server.password), files=form_data)
    if resp.status_code != 200:
        raise Exception("Failed to get " + url)
    if options.raw:
        sys.stdout.write(resp.content + '\n')
    tree = ElementTree.fromstring(resp.content)
    return parse_packages(tree)


def list_packages(server, options):
    packages = get_packages_list(server, options)
    for pkg in packages:
        if not options.raw:
            sys.stdout.write("{g}\t{pkg}\t{v}\n".format(g=pkg['group'], pkg=pkg['name'], v=pkg['version']))


def parse_packages(tree):
    pkg_elems = tree.find('response').find('data').find('packages').findall('package')
    packages = [parse_package(elem) for elem in pkg_elems]
    return packages


def parse_package(elem):
    ret = dict()
    for sub in elem.getchildren():
        ret[sub.tag] = sub.text
    return ret


def expand_package(server, package_name):
    packages = get_packages_list(server)
    for pkg in packages:
        if package_name == pkg['name']:
            return pkg


def get_version(options, pkg):
    if options.version is not None:
        return options.version
    else:
        return pkg['version']


def get_group(options, pkg):
    if options.group is not None:
        return options.group
    else:
        return pkg['group']


def download_package(server, package_name, options):
    pkg = expand_package(server, package_name)
    version = get_version(options, pkg)
    zipfile = pkg['name'] + '-' + version + '.zip'

    group = get_group(options, pkg)
    path = '/etc/packages/' + group + '/' + zipfile
    url = server.url(path)

    response = requests.get(url, auth=(server.username, server.password))
    f = open(zipfile, 'wb')
    if response.status_code == 200:
        f.write(response.content)
    else:
        sys.stderr.write("error: Failed to download " + url + " because " + str(response.status_code) + "\n")
        if options.raw:
            sys.stderr.write(response.content)
            sys.stderr.write("\n")


def upload_package(server, options):
    """curl -u admin:admin -F file=@"name of zip file" -F name="name of package"
            -F force=true -F install=false http://localhost:4505/crx/packmgr/service.jsp"""
    pass
