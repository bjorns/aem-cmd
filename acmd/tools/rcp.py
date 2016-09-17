# coding: utf-8
import json
import optparse
import random
import string
import sys
import time

import requests

from acmd import OK, USER_ERROR, SERVER_ERROR
from acmd import tool, log, error, warning
from acmd.tools.tool_utils import get_argument, get_command

SERVICE_PATH = '/crx/packmgr/service.jsp'

parser = optparse.OptionParser("acmd rcp [options] [list|fetch] [path]")
parser.add_option("-s", "--source-host",
                  dest="source_host", help="Specify source hostname eg. qa-author:4502")
parser.add_option("-c", "--source-credentials",
                  dest="source_credentials",
                  help="Specify remote server username and password as <u>:<p>, defaults to 'admin:admin'",
                  default='admin:admin')
parser.add_option("-p", "--content-path",
                  dest="content_path", help="Specify content path to copy e.g. /content/geometrixx")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")


@tool('rcp', ['list', 'fetch', 'start', 'rm'])
class VltRcpTool(object):
    """ This tool requires the vault rcp bundle to be installed in both source and target installation

        Documentation: http://jackrabbit.apache.org/filevault/rcp.html#
    """

    def execute(self, server, argv):
        options, args = parser.parse_args(argv)

        action = get_command(args, default='list')
        argument = get_argument(args)

        if action == 'list' or action == 'ls':
            return list_rcp_tasks(server, options)
        elif action == 'fetch':
            return fetch_tree_synchronous(server, options, argument)
        elif action == 'start':
            return start_task(server, argument)
        elif action == 'rm':
            return remove_task(server, argument)
        elif action == 'clear':
            clear_tasks(server)
        else:
            error("Unknown rcp action {a}\n".format(a=action))
            return USER_ERROR


def list_rcp_tasks(server, options):
    status, content = get_task_list(server)
    if status != OK:
        return status
    if options.raw:
        sys.stdout.write("{}\n".format(json.dumps(content, indent=4)))
    else:
        for task in content['tasks']:
            sys.stdout.write("{}\t{}\t{}\n".format(task['id'], task['dst'], task['status']['state']))
    return OK


def get_task_list(server):
    url = server.url("/system/jackrabbit/filevault/rcp")

    log("GETting service {}".format(url))
    resp = requests.get(url, auth=server.auth)

    if resp.status_code != 200:
        error("Failed to list rcp tasks, request returned {}\n".format(resp.status_code))
        return SERVER_ERROR, None

    return OK, resp.json()


def _parse_credentials(creds):
    """ Takes a credentials string '<user>:<pass>' and returns a tuple (<user>,<pass>) """
    parts = creds.split(':')
    if len(parts) != 2:
        error("Failed to parse credentials: {}".format(creds))
        sys.exit(-1)
    return parts[0], parts[1]


def fetch_tree_synchronous(server, options, content_path):
    task_id = _create_task_id()

    status = create_task(server, options, task_id, content_path)
    if status != OK:
        error("Failed to fetch {} from {}".format(content_path, options.source_host))
        return status

    status, task = get_task_status(server, task_id)
    if task['status']['state'] != 'NEW':
        error("Failed to locsate new task {}".format(task_id))
        return SERVER_ERROR

    status = start_task(server, task_id)
    if status != OK:
        error("Failed to fetch {} from {}, task {} did not start".format(content_path, options.source_host, task_id))
        return status

    wait_for_task(server, task_id)

    remove_task(server, task_id)
    return OK


def random_hex(num_chars):
    lst = [random.choice("abcdef" + string.digits) for _ in xrange(num_chars)]
    return ''.join(lst)


def _create_task_id():
    return "rcp-{}".format(random_hex(6))


def create_task(server, options, task_id, content_path):
    """ Create a new task, does not start it """
    log("Creating task {}".format(task_id))
    payload = {
        "cmd": "create",
        "id": task_id,
        "src": "http://{credentials}@{source_host}/crx/-/jcr:root{content_path}".format(
            credentials=options.source_credentials,
            source_host=options.source_host,
            content_path=content_path
        ),
        "dst": content_path,
        "batchsize": 2048,
        "update": True,
        "onlyNewer": False,
        "recursive": True,
        "throttle": 1
    }
    url = server.url("/system/jackrabbit/filevault/rcp")
    resp = requests.post(url, auth=server.auth, json=payload)
    if resp.status_code != 201:
        error("Failed to create task, request returned {} and {}\n".format(resp.status_code, resp.content))
        return SERVER_ERROR

    return OK


def start_task(server, task_id):
    """ Returns OK on success """
    log("Starting task {}".format(task_id))
    status, content = post_command(server, task_id, 'start')
    return status


def remove_task(server, task_id):
    """ Delete task - returns OK on success """
    log("Removing task {}".format(task_id))
    status, _ = post_command(server, task_id, 'remove')
    return status


def clear_tasks(server):
    """ Remove all tasks """
    status, content = get_task_list(server)
    if status != OK:
        return status
    for task in content['tasks']:
        status = remove_task(server, task['id'])
        if status != OK:
            warning("Failed to remove task {}".format(task['id']))

    return OK


def get_task_status(server, task_id):
    """ Return all data on a single task """
    status, content = get_task_list(server)
    for task in content['tasks']:
        if task['id'] == task_id:
            return OK, task
    return SERVER_ERROR, None


def wait_for_task(server, task_id):
    """ Wait until task finishes """
    is_running = True
    while is_running:
        status, task = get_task_status(server, task_id)
        is_running = task['status']['state'] == 'RUNNING'
        time.sleep(1)
    return OK


def post_command(server, task_id, cmd):
    """ Generic function for sending simple POST requests """

    payload = {
        'id': task_id,
        'cmd': cmd
    }

    url = server.url("/system/jackrabbit/filevault/rcp")
    log("POSTting service {}, payload {}".format(url, json.dumps(payload)))
    resp = requests.post(url, auth=server.auth, json=payload)

    if resp.status_code != 200:
        error(
            "Failed to send command {cmd} to rcp task {taskid}, request returned {status} and {content}\n".format(
                cmd=cmd,
                taskid=task_id,
                status=resp.status_code,
                content=resp.content
            ))
        return SERVER_ERROR, resp.json()

    return OK, resp.json()
