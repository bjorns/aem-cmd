# coding: utf-8
import json
import optparse
import sys

import requests

from acmd import USER_ERROR, SERVER_ERROR, OK
from acmd import tool, log, error
from acmd.tools.tool_utils import get_argument, get_command, create_task_id

parser = optparse.OptionParser("acmd workflows [options] [list|start]")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")

MODELS_PATH = "/etc/workflow/models.json"
INSTANCES_PATH = '/etc/workflow/instances'

@tool('workflows', ['list', 'start'])
class WorkflowsTool(object):
    """
     See: https://docs.adobe.com/docs/en/cq/5-6-1/workflows/wf-extending/wf-rest-api.html
    """
    @staticmethod
    def execute(server, argv):
        options, args = parser.parse_args(argv)
        action = get_command(args)
        actionarg = get_argument(args)

        if action == 'list' or action == 'ls':
            return list_workflows(server, options)
        elif action == 'start':
            model = actionarg
            path = get_argument(args, i=3)
            return start_workflow(server, options, model, path)
        else:
            error('error: Unknown workflows action {a}\n'.format(a=action))
            return USER_ERROR


def _get_name(model):
    name = model.replace('/etc/workflow/models/', '').replace('/jcr:content/model', '')
    return name


def list_workflows(server, options):
    url = server.url(MODELS_PATH)
    resp = requests.get(url, auth=server.auth)
    if resp.status_code != 200:
        error("Unexpected error code {code}: {content}".format(resp.status_code, resp.content))
        return SERVER_ERROR
    data = resp.json()
    if options.raw:
        sys.stdout.write(json.dumps(data, indent=4))
    else:
        for model_item in data:
            model_name = _get_name(model_item['uri'])
            sys.stdout.write("{}\n".format(model_name))
    return OK


def start_workflow(server, options, model, path):
    task_id = create_task_id(model)
    form_data = dict(
        model='/etc/workflow/models/{}/jcr:content/model'.format(model),
        payload='{}/jcr:content/renditions/original'.format(path),
        payloadType='JCR_PATH',
        workflowTitle=task_id,
        startComment=''
    )
    url = server.url(INSTANCES_PATH)
    resp = requests.post(url, auth=server.auth, data=form_data)
    if resp.status_code != 201:
        error("Unexpected error code {code}: {content}".format(code=resp.status_code, content=resp.content))
        return SERVER_ERROR
    if options.raw:
        sys.stdout.write(resp.content)
    else:
        sys.stdout.write(task_id)
