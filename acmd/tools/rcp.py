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
from acmd.tools.bundles import get_bundle_list
from acmd.tools.tool_utils import get_argument, get_command

SERVICE_PATH = '/crx/packmgr/service.jsp'

parser = optparse.OptionParser("acmd rcp [options] [list|fetch] [path]")
parser.add_option("-s", "--source-host",
                  dest="source_host", help="Specify source hostname eg. qa-author:4502")
parser.add_option("-c", "--source-credentials",
                  dest="source_credentials",
                  help="Specify remote server username and password as <u>:<p>, defaults to 'admin:admin'",
                  default='admin:admin')
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")
parser.add_option("-f", "--force",
                  action="store_const", const=True, dest="force",
                  help="Skip security checks when running tasks")


@tool('rcp', ['list', 'fetch', 'start', 'stop', 'rm'])
class VltRcpTool(object):
    """ This tool requires the vault rcp bundle to be installed in both source and target installation

        Documentation: http://jackrabbit.apache.org/filevault/rcp.html#
    """

    @staticmethod
    def execute(server, argv):
        options, args = parser.parse_args(argv)

        action = get_command(args, default='list')
        argument = get_argument(args, i=2)
        argument2 = get_argument(args, i=3, default=argument)

        if action == 'list' or action == 'ls':
            return list_rcp_tasks(server, options)
        if action == 'create':
            src_path = argument
            dst_path = argument2
            return create_new_task(server, src_path, dst_path, options)
        elif action == 'start':
            return start_task(server, argument, options)
        elif action == 'stop':
            return stop_task(server, argument, options)
        elif action == 'remove' or action == 'rm':
            return remove_task(server, argument)
        elif action == 'clear':
            return clear_tasks(server)
        elif action == 'fetch':
            return fetch_tree_synchronous(server, options, argument)
        else:
            error("Unknown rcp action {a}".format(a=action))
            return USER_ERROR


def list_rcp_tasks(server, options):
    def _get_path(url):
        parts = url.split('/jcr:root')
        return parts[1]

    def _get_hostname(url):
        parts = url.split('/crx')
        if len(parts) < 2:
            warning("Failed to split src url {}".format(url))
            return url
        host = parts[0]
        parts = host.split('@')
        if len(parts) < 2:
            warning("Failed to retrieve hostname from url {}".format(url))
            return url
        return parts[1]

    status, content = _get_task_list(server)
    if status != OK:
        return status
    if options.raw:
        sys.stdout.write("{}\n".format(json.dumps(content, indent=4)))
    else:
        for task in content['tasks']:
            sys.stdout.write("{id}\t{src}{src_path}\t{dst_path}\t{status}\n".format(
                id=task['id'], src=_get_hostname(task['src']),
                src_path=_get_path(task['src']), dst_path=task['dst'], status=task['status']['state']))
    return OK


def _get_task_list(server):
    url = server.url("/system/jackrabbit/filevault/rcp")

    log("GETting service {}".format(url))
    resp = requests.get(url, auth=server.auth)

    if resp.status_code != 200:
        error("Failed to list rcp tasks, request returned {}".format(resp.status_code))
        return SERVER_ERROR, None

    return OK, resp.json()


def create_new_task(server, src_path, dst_path, options):
    if options.source_host is None:
        error("Missing argument source host (-s)")
        return USER_ERROR

    task_id = _create_task_id()

    status, data = _create_task(server, task_id, src_path, dst_path, options)
    if status != OK:
        error("Failed to fetch {} from {}".format(src_path, options.source_host))
        return status

    if options.raw:
        sys.stdout.write("{}\n".format(json.dumps(data)))
    else:
        sys.stdout.write("{}\n".format(data['id']))
    return OK


def random_hex(num_chars):
    lst = [random.choice("abcdef" + string.digits) for _ in xrange(num_chars)]
    return ''.join(lst)


def _create_task_id():
    return "rcp-{}".format(random_hex(6))


def _create_task(server, task_id, src_path, dst_path, options):
    """ Create a new task, does not start it """
    log("Creating task {}".format(task_id))
    payload = {
        "cmd": "create",
        "id": task_id,
        "src": "http://{credentials}@{source_host}/crx/-/jcr:root{content_path}".format(
            credentials=options.source_credentials,
            source_host=options.source_host,
            content_path=src_path
        ),
        "dst": dst_path,
        "batchsize": 2048,
        "update": True,
        "onlyNewer": False,
        "recursive": True,
        "throttle": 1
    }
    url = server.url("/system/jackrabbit/filevault/rcp")
    resp = requests.post(url, auth=server.auth, json=payload)
    if resp.status_code != 201:
        error("Failed to create task, request returned {} and {}".format(resp.status_code, resp.content))
        return SERVER_ERROR, None

    return OK, resp.json()


def get_bundle_status(server, bundle_name):
    bundle_list = get_bundle_list(server)
    for bundle in bundle_list:
        if bundle['symbolicName'] == bundle_name:
            return bundle
    raise Exception("Failed to locate bundle {}".format(bundle_name))


def start_task(server, task_id, options):
    """ Returns OK on success """
    if not options.force:
        bundle = get_bundle_status(server, 'com.adobe.granite.workflow.core')
        if bundle['state'] == 'Active':
            error("Do not run rcp when workflow bundle(com.adobe.granite.workflow.core)" +
                  " is active. It might bog down the server in unnecessary workflow.")
            return SERVER_ERROR

    log("Starting task {}".format(task_id))
    status, content = post_command(server, task_id, 'start')

    if options.raw:
        sys.stderr.write("{}\n".format(json.dumps(content)))
    return status


def stop_task(server, task_id, options):
    """ Returns OK on success """
    log("Stopping task {}".format(task_id))
    status, content = post_command(server, task_id, 'stop')
    if options.raw:
        sys.stderr.write("{}\n".format(json.dumps(content)))
    return status


def remove_task(server, task_id):
    """ Delete task - returns OK on success """
    log("Removing task {}".format(task_id))
    status, _ = post_command(server, task_id, 'remove')
    return status


def clear_tasks(server):
    """ Remove all tasks """
    status, content = _get_task_list(server)
    if status != OK:
        return status
    for task in content['tasks']:
        status = remove_task(server, task['id'])
        if status != OK:
            warning("Failed to remove task {}".format(task['id']))

    return OK


def get_task_status(server, task_id):
    """ Return all data on a single task """
    status, content = _get_task_list(server)
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
            "Failed to send command {cmd} to rcp task {taskid}, request returned {status} and {content}".format(
                cmd=cmd,
                taskid=task_id,
                status=resp.status_code,
                content=resp.content
            ))
        return SERVER_ERROR, resp.json()
    return OK, resp.json()


def fetch_tree_synchronous(server, options, content_path):
    """ Compount tool for fetching data immediately.
        Performs: Create, Fetch, Wait, Remove
    """
    task_id = _create_task_id()

    status, data = _create_task(server, task_id, content_path, content_path, options)
    if status != OK:
        error("Faiiled to fetch {} from {}".format(content_path, options.source_host))
        return status

    status, task = get_task_status(server, task_id)
    log("Debug {}".format(json.dumps(task, indent=4)))
    if task['status']['state'] != 'NEW':
        error("Failed to locsate new task {}".format(task_id))
        return SERVER_ERROR

    status = start_task(server, task_id, options)
    if status != OK:
        error("Failed to fetch {} from {}, task {} did not start".format(content_path, options.source_host, task_id))
        return status

    wait_for_task(server, task_id)

    remove_task(server, task_id)
    return OK
