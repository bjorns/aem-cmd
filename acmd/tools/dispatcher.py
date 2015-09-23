# coding: utf-8
import sys
import optparse
from urlparse import urlparse
from acmd import tool, log, SERVER_ERROR

import requests

from acmd.tools.tool_utils import get_action

parser = optparse.OptionParser("acmd dispatcher [options] [clear]")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")


@tool('dispatcher', ['clear'])
class DispatcherTool(object):
    def execute(self, server, argv):
        (options, args) = parser.parse_args(argv)
        action = get_action(args, 'help')
        if action == 'clear':
            clear_cache(server, options)
        else:
            parser.print_help()

def clear_cache(server, options):
    host_url = urlparse(server.host)

    headers = {
        'Host': host_url.hostname,
        'CQ-Action': 'DELETE',
        'CQ-Handle': '/',
        'CQ-Path': '/'
    }

    host = server.dispatcher if server.dispatcher is not None else server.host
    url = '{host}{path}'.format(host=host, path='/dispatcher/invalidate.cache')
    log("Clearing cache with request to {}".format(url))
    response = requests.get(url, auth=server.auth, headers=headers)
    if response.status_code != 200:
        sys.stderr.write("error: " + str(response.status_code) + "\n")
        return SERVER_ERROR
    if "<H1>OK</H1>" not in response.content:
        sys.stderr.write("error: Failed to validate response '{}'\n".format(response.content.strip()))
        return SERVER_ERROR

    if options.raw:
        sys.stdout.write(response.content + "\n")
    else:
        sys.stdout.write("OK\n")
