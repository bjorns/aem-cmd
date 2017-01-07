# coding: utf-8
import sys

import requests

from acmd import log, error
from acmd import SERVER_ERROR, OK
from acmd.tools.tool_utils import create_task_id

MODELS_PATH = "/etc/workflow/models.json"
INSTANCES_PATH = '/etc/workflow/instances'


class WorkflowsApi(object):
    def __init__(self, server, raw=False):
        self.server = server
        self.raw = raw

    def start_workflow(self, model, path):
        """      curl -u admin:admin -d "model=/etc/workflow/models/request_for_activation/jcr:content/model&payload=/content/geometrixx/en/company&payloadType=JCR_PATH&workflowTitle=myWorkflowTitle" http://localhost:4502/etc/workflow/instances

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
