# coding: utf-8
import sys
import optparse
import requests
import json

from acmd.commands.registry import register_command
from acmd.http_util import get_json, post_form

parser = optparse.OptionParser("acmd packages [options] [upload] [<zip>|<package>]")
parser.add_option("-v", "--verbose",
                action="store_const", const=True, dest="verbose",
                help="report verbose data when supported")


class PackagesCommand(object):
    def __init__(self):
        self.name = 'packages'

    def execute(self, server, argv):
        (options, args) = parser.parse_args(argv)

        action = get_action(args)
        actionarg = get_argument(args)
        if action == 'upload':
            upload_package(server, options)
        else:
            sys.stderr.write('error: Unknown bundle action {a}\n'.format(a=action))
            sys.exit(-1)


def upload_package(server, options):
    """curl -u admin:admin -F file=@"name of zip file" -F name="name of package"
            -F force=true -F install=false http://localhost:4505/crx/packmgr/service.jsp"""
    pass


cmd = PackagesCommand()
register_command(cmd)
