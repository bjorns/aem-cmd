# coding: utf-8
import json
from httmock import urlmatch


class MockWorkflowsService(object):
    def __init__(self):
        self.models = []
        self.instances = []

    def add_model(self, model):
        wf = {'uri': '/etc/workflow/models/{}/jcr:content/model'.format(model)}
        self.models.append(wf)

    def add_instance(self, instance):
        wf = {'uri': '/etc/workflow/instances/server0/2017-01-05/update_asset_{}'.format(instance)}
        self.instances.append(wf)


class MockWorkflowHttpService(object):
    def __init__(self, task_service=None):
        self.wf_service = task_service if task_service is not None else MockWorkflowsService()
        self.request_log = []

    @urlmatch(netloc='localhost:4502')
    def __call__(self, url, request):
        self.request_log.append(request)
        if request.method == 'GET':
            if 'models' in url.path:
                return json.dumps(self.wf_service.models)
            elif 'instances' in url.path:
                return json.dumps(self.wf_service.instances)
        elif request.method == 'POST':
            return self._handle_post()

    def _handle_post(self):
        model = 'foo'
        self.wf_service.add_model(model)

        return {
            'status_code': 201,
            'content': ''
        }
