# coding: utf-8
import sys
import json
import optparse
import requests

from acmd import tool, get_json



parser = optparse.OptionParser("acmd search [options] <property>=<value>")
parser.add_option("-l", "--limit", type="int",
                  dest="limit", help="limit number of hits", default=-1)
parser.add_option("-p", "--path",
                  dest="path", help="root JCR path to search", default="/")
parser.add_option("-v", "--verbose",
                  action="store_const", const=True, dest="verbose",
                  help="report verbose data when supported")


PATH ='/bin/querybuilder.json'


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
    i = 1
    params = dict()
    for arg in args:
        key, val = arg.split('=')
        params[str(i) + '_property'] = key
        params[str(i) + '_property.value'] = val
        i = i + 1
    return params

def search(server, options, props):
    status, resp = get_json(server, PATH, props)
    if status != 200:
        sys.stderr.write("error: Failed to perform search: " + str(resp))
    elif options.verbose:
        sys.stdout.write(json.dumps(resp, indent=4))
    else:
        assert resp.get('success') == True
        assert options.limit == -1 or options.limit >= resp.get('results')
        hits = resp.get('hits', [])
        for hit in hits:
            path = hit.get('path', '').strip()
            if len(path) > 0:
                sys.stdout.write("{}\n".format(path))
