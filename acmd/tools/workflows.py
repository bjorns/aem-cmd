# coding: utf-8
import optparse
import sys
import json

import requests

from acmd import USER_ERROR, SERVER_ERROR
from acmd import tool
from acmd.tools.tool_utils import get_argument, get_command

parser = optparse.OptionParser("acmd workflows [options] [list|start]")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")


MODELS_PATH = "/etc/workflow/models.json"


@tool('workflows', ['list', 'start'])
class WorkflowsTool(object):
    @staticmethod
    def execute(server, argv):
        options, args = parser.parse_args(argv)

        action = get_command(args)
        actionarg = get_argument(args)

        if action == 'list' or action == 'ls':
            return list_workflows(server, options)
        elif action == 'start':
            return start_workflow(server, options, actionarg)
        else:
            sys.stderr.write('error: Unknown workflows action {a}\n'.format(a=action))
            return USER_ERROR



def _get_name(model):
    name = model.replace('/etc/workflow/models/', '').replace('/jcr:content/model', '')
    return name


def list_workflows(server, options):
    url = server.url(MODELS_PATH)
    resp = requests.get(url, auth=(server.username, server.password))
    if resp.status_code != 200:
        sys.stderr.write(resp.content)
        return SERVER_ERROR
    data = resp.json()
    if options.raw:
        sys.stdout.write(json.dumps(data, indent=4))
    else:
        for model_item in data:
            model_name = _get_name(model_item['uri'])
            sys.stdout.write("{}\n".format(model_name))



def start_workflow(server, options, model):
    pass
