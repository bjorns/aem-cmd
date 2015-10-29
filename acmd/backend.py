# coding: utf-8
""" Support for running groovy scripts on the backend. Note that this module requires the aem-groovy-console bundle
    to be installed on the instance.

    https://github.com/Citytechinc/cq-groovy-console
    """
from acmd import OK, SERVER_ERROR

import requests

from acmd.logger import log, warning

STACKTRACE_FIELD = 'stacktrace'
OUTPUT_FIELD = 'output'
RESULT_FIELD = 'result'

SERVICE_PATH = "/bin/groovyconsole/post.json"


def execute(server, script, args, raw_output=False):
    """ Execute the script string on server using args
        Note: args[0] is expected to be the filename of the script.

        Returns a tuple (status, data) where data is the parsed json
        object if status is OK, otherwise it is the raw response
        content.
    """
    url = server.url(SERVICE_PATH)

    script = _replace_vars(script, args)
    form_data = dict(
        script=script
    )

    log("Posting groovy script to {}".format(url))
    resp = requests.post(url, auth=server.auth, data=form_data)
    if resp.status_code == 200:
        data = resp.json()
        output = _clean_output(data) if not raw_output else data
        return OK, output
    else:
        return SERVER_ERROR, resp.content


def _clean_output(data):
    """ Older versions of the groovy console had different field names so we try and unify it: """
    ret = dict()
    ret[RESULT_FIELD] = data['result'] if 'result' in data else data['executionResult']

    if 'stacktraceText' in data and data['stacktraceText'] != '':
        ret[STACKTRACE_FIELD] = data['stacktraceText']
    elif 'exceptionStackTrace' in data and data['exceptionStackTrace'] != '':
        ret[STACKTRACE_FIELD] = data['exceptionStackTrace']

    if 'outputText' in data and data['outputText'] != '':
        ret[OUTPUT_FIELD] = data['outputText']
    elif 'output' in data and data['output'] != '':
        ret[OUTPUT_FIELD] = data['output']
    else:
        warning("Unexpected format of return data from groovy console: {}".format(data))
    return ret


def _replace_vars(script, args):
    """ Replace instances of 'args[0], args[1] with the content of the args object by
        preprocessing the script contents.
    """
    return script
