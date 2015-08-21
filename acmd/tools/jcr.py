# coding: utf-8
import sys
import optparse
import json

from acmd.tool import tool
from acmd.tools.tool_utils import *
from acmd.http_util import get_json

parser = optparse.OptionParser("acmd jcr [options] [find|ls] <jcr path>")
parser.add_option("-v", "--verbose",
                  action="store_const", const=True, dest="verbose",
                  help="report verbose data when supported")


@tool('jcr')
class JcrTool(object):
    def execute(self, server, argv):
        options, args = parser.parse_args(argv)

        action = get_action(args, 'ls')
        path = get_argument(args)

        if action == 'ls':
            list_path(server, options, path)


def is_property(path_segment, data):
    return isinstance(data, basestring)


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
