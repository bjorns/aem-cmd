# coding: utf-8
import requests
import json

from acmd import SERVER_ERROR, USER_ERROR, OK
from acmd import error
from acmd.tools.tool_utils import create_task_id

MODELS_PATH = "/etc/workflow/models.json"
INSTANCES_PATH = '/etc/workflow/instances'

INSTANCE_MODES = {'RUNNING', 'SUSPENDED', 'ABORTED', 'COMPLETED'}


class WorkflowsApi(object):
    def __init__(self, server, raw=False):
        self.server = server
        self.raw = raw

    def start_workflow(self, model, path):
        """ curl -u admin:admin
                -d "model=/etc/workflow/models/request_for_activation/jcr:content/model&
                payload=/content/geometrixx/en/company&
                payloadType=JCR_PATH&
                workflowTitle=myWorkflowTitle" http://localhost:4502/etc/workflow/instances

        """
        task_id = create_task_id(model)

        form_data = dict(
            model='/etc/workflow/models/{}/jcr:content/model'.format(model),
            payload=path,
            payloadType='JCR_PATH',
            workflowTitle=task_id,
            startComment=''
        )

        url = self.server.url(INSTANCES_PATH)
        resp = requests.post(url, auth=self.server.auth, data=form_data)
        if resp.status_code != 201:
            error("Unexpected error code {code}: {content}".format(
                code=resp.status_code, content=resp.content))
            return SERVER_ERROR

        output = resp.content if self.raw else task_id
        return OK, output

    def get_instances(self, mode):
        if mode not in INSTANCE_MODES:
            return USER_ERROR, "Unknown instance mode {}".format(mode)

        path = "/etc/workflow/instances.{mode}.json".format(mode=mode)
        url = self.server.url(path)
        resp = requests.get(url, auth=self.server.auth)
        if resp.status_code != 200:
            error("Unexpected error code {code}: {content}".format(
                code=resp.status_code, content=resp.content))
            return SERVER_ERROR, []

        return OK, json.loads(resp.content)
