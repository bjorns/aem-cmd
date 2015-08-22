# coding: utf-8
import sys
import json
import optparse

import requests

from acmd import tool

parser = optparse.OptionParser("acmd search [options] <property>=<value>")
parser.add_option("-l", "--limit", type="int",
                  dest="limit", help="limit number of hits", default=-1)
parser.add_option("-p", "--path",
                  dest="path", help="root JCR path to search", default="/")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")

PATH = '/bin/querybuilder.json'


@tool('search')
class SearchTool(object):
    def execute(self, server, argv):
        (options, args) = parser.parse_args(argv)
        if len(args) < 2:
            parser.print_help()
        else:
            params = parse_params(args[1:])
            params['p.limit'] = options.limit
            params['path'] = options.path
            search(server, options, params)


def parse_params(args):
    params = dict()
    for i, arg in enumerate(args):
        key, val = arg.split('=')
        params[str(i + 1) + '_property'] = key
        params[str(i + 1) + '_property.value'] = val
    return params


def search(server, options, params):
    url = server.url(PATH)
    resp = requests.get(url, auth=(server.username, server.password), params=params)

    if resp.status_code != 200:
        sys.stderr.write("error: Failed to perform search: " + str(resp))
    elif options.raw:
        sys.stdout.write(json.dumps(resp, indent=4))
    else:
        data = resp.json()
        assert data.get('success') is True

        assert options.limit == -1 or options.limit >= data.get('results')
        hits = data.get('hits', [])
        for hit in hits:
            path = hit.get('path', '').strip()
            if len(path) > 0:
                sys.stdout.write("{}\n".format(path))
