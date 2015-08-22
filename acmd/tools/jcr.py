# coding: utf-8
import sys
import optparse
import json

from acmd import tool, get_json


parser = optparse.OptionParser("acmd <ls|cat> [options] <jcr path>")
parser.add_option("-v", "--verbose",
                  action="store_const", const=True, dest="verbose",
                  help="report verbose data when supported")


@tool('ls')
class ListTool(object):
    """ Since jcr operations are considered so common we extract what would otherwise be
        a jcr tool into separate smaller tools for ease of use.
    """
    def execute(self, server, argv):
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
    status, obj = get_json(server, "{path}.1.json".format(path=path))
    if status != 200:
        sys.stderr.write("error: Failed to get path {}, request returned {}\n".format(path, status))
        sys.exit(-1)
    if options.verbose:
        sys.stdout.write(json.dumps(obj, indent=4))
    else:
        for path_segment, data in obj.items():
            if not is_property(path_segment, data):
                sys.stdout.write("{local}\n".format(path=path, local=path_segment))


def cat_node(server, options, path):
    status, obj = get_json(server, "{path}.1.json".format(path=path))
    if status != 200:
        sys.stderr.write("error: Failed to get path {}, request returned {}\n".format(path, status))
        sys.exit(-1)
    if options.verbose:
        sys.stdout.write(json.dumps(obj, indent=4))
    else:
        for prop, data in obj.items():
            if is_property(prop, data):
                sys.stdout.write("{key}:\t{value}\n".format(key=prop, value=data))
