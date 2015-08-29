# coding: utf-8
import sys
import os.path
import optparse
import json

import requests

from acmd import tool, log

parser = optparse.OptionParser("acmd <ls|cat|find> [options] <jcr path>")
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


@tool('find')
class FindTool(object):
    def execute(self, server, argv):
        options, args = parser.parse_args(argv)
        path = args[1] if len(args) >= 2 else '/'
        list_tree(server, options, path)


def list_tree(server, options, path):
    nodes = _get_subnodes(server, path)
    _list_nodes(path, nodes, abs=True)
    for path_segment, data in nodes.items():
        if not is_property(path_segment, data):
            list_tree(server, options, os.path.join(path, path_segment))


def list_path(server, options, path):
    data = _get_subnodes(server, path)
    if options.raw:
        sys.stdout.write("{}\n".format(json.dumps(data, indent=4)))
    else:
        _list_nodes(path, data, full_path=options.full_path)


def _list_nodes(path, nodes, full_path=False):
    for path_segment, data in nodes.items():
        if not is_property(path_segment, data):
            if full_path:
                sys.stdout.write("{path}\n".format(path=os.path.join(path, path_segment)))
            else:
                sys.stdout.write("{path}\n".format(path=path_segment))


def _get_subnodes(server, path):
    url = server.url("{path}.1.json".format(path=path))

    log("GETting service {}".format(url))
    resp = requests.get(url, auth=server.auth)

    if resp.status_code != 200:
        sys.stderr.write("error: Failed to get path {}, request returned {}\n".format(path, resp.status_code))
        sys.exit(-1)

    return resp.json()


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
                if type(data) == str:
                    data = data.encode('utf-8')
                sys.stdout.write("{key}:\t{value}\n".format(key=prop, value=data))


def is_property(path_segment, data):
    return not isinstance(data, dict)
