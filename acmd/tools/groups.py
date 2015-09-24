# coding: utf-8
import json
import sys
import optparse

import requests

from lxml import html

from acmd import tool
from acmd import USER_ERROR, SERVER_ERROR, OK, error
from acmd.tools.tool_utils import get_action, get_argument, filter_system


parser = optparse.OptionParser("acmd groups <list|create|adduser> [options] <groupname> <username>")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")
parser.add_option("-c", "--compact",
                  action="store_const", const=True, dest="compact",
                  help="output only package name")


@tool('groups', ['list', 'create', 'adduser'])
class GroupsTool(object):
    def execute(self, server, argv):
        options, args = parser.parse_args(argv)
        action = get_action(args, 'list')
        groupname = get_argument(args)
        if action == 'list':
            return list_groups(server, options)
        elif action == 'create':
            return create_group(server, options, groupname)
        if action == 'adduser':
            username = get_argument(args, 3)
            return add_user(server, options, groupname, username)
        else:
            parser.print_help()
            return USER_ERROR


def create_group(server, options, name):
    """ curl -u admin:admin -FcreateGroup=group1 -FauthorizableId=testGroup1
            http://localhost:4502/libs/granite/security/post/authorizables
    """
    assert len(name) > 0
    form_data = {
        'createGroup': '',
        'authorizableId': name
    }
    url = server.url('/libs/granite/security/post/authorizables')
    resp = requests.post(url, auth=server.auth, data=form_data)
    if resp.status_code != 201:
        error("Failed to create group: {}".format(resp.content))
        return SERVER_ERROR
    if options.raw:
        sys.stdout.write("{}\n".format(resp.content))
    else:
        tree = html.fromstring(resp.text)
        path = tree.xpath('//div[@id="Path"]/text()')[0]
        sys.stdout.write("{}\n".format(path))
    return OK


def get_group_path(groupname):
    return "/home/groups/{c}/{name}".format(c=groupname[0], name=groupname)


def add_user(server, options, groupname, username):
    """ curl -u admin:admin -FaddMembers=testuser1
            http://localhost:4502/home/groups/t/testGroup.rw.html """
    group_path = get_group_path(groupname)
    path = "{}.rw.html".format(group_path)
    url = server.url(path)
    props = {'addMembers': username}
    resp = requests.post(url, auth=server.auth, data=props)
    if resp.status_code != 200:
        error("Failed to add user: {}".format(resp.content))
        return SERVER_ERROR
    if options.raw:
        sys.stdout.write("{}\n".format(resp.content))
    else:
        tree = html.fromstring(resp.text)
        path = tree.xpath('//div[@id="Path"]/text()')[0]
        sys.stdout.write("{}\n".format(path))
    return OK


def list_groups(server, options):
    url = server.url('/home/groups.2.json')
    resp = requests.get(url, auth=server.auth)
    if resp.status_code != 200:
        error("Failed to get groups list:\n{}\n".format(resp.content))
        return SERVER_ERROR
    data = resp.json()
    if options.raw:
        sys.stdout.write("{}\n".format(json.dumps(data, indent=4)))
    elif options.compact:
        for initial, group in filter_system(data.items()):
            for groupname, userdata in filter_system(group.items()):
                sys.stdout.write("{}\n".format(groupname))
    else:
        sys.stdout.write("Available groups:\n")
        for initial, group in filter_system(data.items()):
            for username, userdata in filter_system(group.items()):
                sys.stdout.write("    {}\n".format(username))
    return OK
