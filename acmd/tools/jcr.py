# coding: utf-8
import sys
import optparse
import json

import requests

from acmd import tool, log

parser = optparse.OptionParser("acmd <ls|cat> [options] <jcr path>")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")
parser.add_option("-p", "--fullpath",
                  action="store_const", const=True, dest="full_path",
                  help="output full paths instead of local")


@tool('ls')
class ListTool(object):
    """ Since jcr operations are considered so common we extract what would otherwise be
        a jcr tool into separate smaller tools for ease of use.
    """

    def execute(self, server, argv):
        log("Executing {}".format(self.name))
        options, args = parser.parse_args(argv)
        path = args[1] if len(args) >= 2 else '/'
        list_path(server, options, path)


@tool('cat')
class InspectTool(object):
    def execute(self, server, argv):
        options, args = parser.parse_args(argv)
        path = args[1] if len(args) >= 2 else '/'
        cat_node(server, options, path)


def is_property(path_segment, data):
    return not isinstance(data, dict)


def list_path(server, options, path):
    url = server.url("{path}.1.json".format(path=path))

    log("GETting service {}".format(url))
    resp = requests.get(url, auth=server.auth)

    if resp.status_code != 200:
        sys.stderr.write("error: Failed to get path {}, request returned {}\n".format(path, resp.status_code))
        sys.exit(-1)

    data = resp.json()
    if options.raw:
        sys.stdout.write("{}\n".format(json.dumps(data, indent=4)))
    else:
        for path_segment, data in data.items():
            if not is_property(path_segment, data):
                if options.full_path:

                    sys.stdout.write("{path}\n".format(path=join_paths(path, path_segment)))
                else:
                    sys.stdout.write("{local}\n".format(local=path_segment))


def join_paths(path, local):
    if path.endswith('/'):
        return path + local
    else:
        return path + '/' + local


def cat_node(server, options, path):
    url = server.url("{path}.1.json".format(path=path))
    resp = requests.get(url, auth=server.auth)
    if resp.status_code != 200:
        sys.stderr.write("error: Failed to get path {}, request returned {}\n".format(path, resp.status_code))
        sys.exit(-1)
    data = resp.json()
    if options.raw:
        sys.stdout.write("{}\n".format(json.dumps(data, indent=4)))
    else:
        for prop, data in data.items():
            if is_property(prop, data):
                sys.stdout.write("{key}:\t{value}\n".format(key=prop, value=data.encode('utf-8')))
