# coding: utf-8
import sys
import optparse
import json
import requests

from lxml import html

from acmd import tool
from acmd import USER_ERROR, SERVER_ERROR, OK, error
from acmd import parse_properties
from acmd.tools.tool_utils import get_action, get_argument, filter_system

parser = optparse.OptionParser("acmd users <list|create|setprop> [options] <username> [arguments]")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")
parser.add_option("-p", "--password",
                  dest="password", help="Set password of the user")
parser.add_option("-c", "--compact",
                  action="store_const", const=True, dest="compact",
                  help="output only package name")


@tool('users', ['list', 'create', 'setprop'])
class UserTool(object):
    def execute(self, server, argv):
        options, args = parser.parse_args(argv)
        action = get_action(args, 'list')
        actionarg = get_argument(args)
        if action == 'list' or action == 'ls':
            return list_users(server, options)
        elif action == 'create':
            return create_user(server, options, actionarg)
        elif action == 'setprop':
            username = actionarg
            propstring = get_argument(argv, 3)
            props = parse_properties(propstring)
            return set_profile_properties(server, options, username, props)
        else:
            parser.print_help()
            return USER_ERROR


def list_users(server, options):
    url = server.url('/home/users.2.json')
    resp = requests.get(url, auth=server.auth)
    if resp.status_code != 200:
        error("Failed to get users list:\n{}\n".format(resp.content))
        return SERVER_ERROR
    data = resp.json()
    if options.raw:
        sys.stdout.write("{}\n".format(json.dumps(data, indent=4)))
    if options.compact:
        for initial, group in filter_system(data.items()):
            for username, userdata in filter_system(group.items()):
                sys.stdout.write("{}\n".format(username))
    else:
        sys.stdout.write("Available users:\n")
        for initial, group in filter_system(data.items()):
            for username, userdata in filter_system(group.items()):
                sys.stdout.write("    {}\n".format(username))
    return OK


def create_user(server, options, username):
    """ curl -u admin:admin -FcreateUser= -FauthorizableId=testuser -Frep:password=abc123
            http://localhost:4502/libs/granite/security/post/authorizables """
    assert len(username) > 0
    form_data = {
        'createUser': '',
        'authorizableId': username,
        'rep:password': options.password
    }
    url = server.url('/libs/granite/security/post/authorizables')
    resp = requests.post(url, auth=server.auth, data=form_data)
    if resp.status_code != 201:
        error("Failed to create user: {}".format(resp.content))
        return SERVER_ERROR
    if options.raw:
        sys.stdout.write("{}\n".format(resp.content))
    else:
        tree = html.fromstring(resp.text)
        path = tree.xpath('//div[@id="Path"]/text()')[0]
        sys.stdout.write("{}\n".format(path))
    return OK


def get_user_path(username):
    return "/home/users/{c}/{name}".format(c=username[0], name=username)


def set_profile_properties(server, options, username, props):
    """ curl -u admin:admin -Fprofile/age=29 http://localhost:4502/home/users/t/testuser1.rw.html """

    user_path = get_user_path(username)
    path = "{}.rw.html".format(user_path)
    url = server.url(path)
    props = {'profile/' + k: v for k, v in props.items()}
    resp = requests.post(url, auth=server.auth, data=props)
    if resp.status_code != 200:
        sys.stderr.write("error: Failed to set profile property on path {}, request returned {}\n".format(path, resp.status_code))
        return SERVER_ERROR
    if options.raw:
        sys.stdout.write("{}\n".format(resp.content))
    else:
        sys.stdout.write("{}\n".format(user_path))
    return OK
