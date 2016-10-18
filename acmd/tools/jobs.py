# coding: utf-8
import sys
import optparse
import requests

from acmd import tool, error
from acmd.tools import get_command, get_argument


QUERYBUILDER_PATH = '/bin/querybuilder.json'


parser = optparse.OptionParser("acmd jobs [options] <pending|all>")

all_params = {
    'path': '/var/eventing/jobs',
    'type': 'slingevent:Job',
    'p.limit': '3',
    #'fulltext': '/com/day/cq/replication/job',
    'fulltext.relPath': '@slingevent:topic',
    'orderby': 'slingevent:created',
    'orderby.sort': 'asc'
}
pending_params = dict(all_params)
pending_params['property.and'] = 'true',
pending_params['property'] = 'slingevent:finished',
pending_params['property.operation'] = 'not',




@tool('jobs')
class JobsTool(object):
    def execute(self, server, argv):
        (options, args) = parser.parse_args(argv)

        action = get_command(args, 'list')
        actionarg = get_argument(args)
        if action == 'all':
            list_all_jobs(server)
        elif action == 'pending':
            list_pending_jobs(server)
        else:
            parser.print_help()


def list_all_jobs(server):
    url = server.url(QUERYBUILDER_PATH)
    resp = requests.get(url, auth=server.auth, params=all_params)
    if resp.status_code != 200:
        error("Failed to list pending jobs from {}".format(url))
    else:
        sys.stdout.write("{}\n".format(resp.content))


def list_pending_jobs(server):
    url = server.url(QUERYBUILDER_PATH)
    resp = requests.get(url, auth=server.auth, params=pending_params)
    if resp.status_code != 200:
        error("Failed to list pending jobs from {}".format(url))
    else:
        sys.stdout.write("{}\n".format(resp.content))


