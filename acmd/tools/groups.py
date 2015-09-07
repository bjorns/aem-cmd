# coding: utf-8
import sys
import optparse

import requests

from lxml import html

from acmd import tool
from acmd import USER_ERROR, SERVER_ERROR, OK, error

parser = optparse.OptionParser("acmd groups <create> [options] <groupname>")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")


@tool('groups')
class GroupsTool(object):
    def execute(self, server, argv):
        options, args = parser.parse_args(argv)
        action = get_action(args)
        actionarg = get_argument(args)
        if action == 'create':
            return create_group(server, options, actionarg)
        else:
            parser.print_help()
            return USER_ERROR


def get_action(argv):
    if len(argv) < 2:
        return 'list'
    else:
        return argv[1]


def get_argument(argv):
    if len(argv) < 3:
        return None
    else:
        return argv[2]


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
