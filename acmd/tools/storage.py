# coding: utf-8
import sys
import optparse
import requests

from acmd import tool, error
from tool_utils import get_action

OPT_PATH = '/system/console/jmx/com.adobe.granite:type=Repository/op/startTarOptimization/'
GC_PATH = '/system/console/jmx/com.adobe.granite:type=Repository/op/runDataStoreGarbageCollection/java.lang.Boolean'

parser = optparse.OptionParser("acmd storage [options] optimize|gc")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")


@tool('storage', ['optimize', 'gc'])
class DatastoreTool(object):
    def execute(self, server, argv):
        (options, args) = parser.parse_args(argv)

        cmd = get_action(args, None)
        if cmd == 'optimize':
            optimize(server, options)
        elif cmd == 'gc':
            garbage_collect(server, options)
        else:
            parser.print_help()


def optimize(server, options):
    url = server.url(OPT_PATH)
    resp = requests.post(url, auth=server.auth)
    if resp.status_code != 200:
        error("Failed to trigger Tar Optimization because: {}".format(resp.content))
        return -1
    else:
        if options.raw:
            sys.stdout.write("{}".format(resp.content))


def garbage_collect(server, options):
    url = server.url(GC_PATH)
    resp = requests.post(url, auth=server.auth)
    if resp.status_code != 200:
        error("Failed to trigger Tar Optimization because: {}".format(resp.content))
        return -1
    else:
        if options.raw:
            sys.stdout.write("{}".format(resp.content))
