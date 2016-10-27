# coding: utf-8
import optparse
import os

import requests

from acmd import OK, SERVER_ERROR
from acmd import tool, error, log
from acmd.tools.tool_utils import get_argument, get_command

parser = optparse.OptionParser("acmd assets <import|touch> [options] <file>")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")


@tool('assets')
class AssetsTool(object):
    """ Manage AEM DAM assets """

    @staticmethod
    def execute(server, argv):
        options, args = parser.parse_args(argv)
        action = get_command(args)
        actionarg = get_argument(args)

        if action == 'import':
            return import_path(server, options, actionarg)
        return OK


def import_path(server, options, path):
    if os.path.isdir(path):
        return import_directory(server, options, path)
    else:
        return import_file(server, options, path)


def import_directory(server, options, path):
    log("Importing file {}".format(path))
    for subdir, dirs, files in os.walk(path):
        # _create_dir(server, subdir)
        for filename in files:
            import_file(server, options, os.path.join(subdir, filename))


def import_file(server, options, filename):
    print filename


# curl -s -u admin:admin -X POST -F "jcr:primaryType=sling:OrderedFolder" $HOST$dampath > /dev/null
def _create_dir(server, path):
    form_data = {'jcr:primaryType': 'sling:OrderedFolder'}
    url = server.url(path)
    resp = requests.post(url, auth=server.auth, data=form_data)
    if resp.status_code != 201:
        error("Failed to create directory {}".format(url))
        return SERVER_ERROR
    return OK
