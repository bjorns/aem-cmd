# coding: utf-8
import json
import optparse

import requests

import sys
from acmd import tool, OK, USER_ERROR, SERVER_ERROR, error

parser = optparse.OptionParser("acmd groups <list|create|adduser> [options] <groupname> <username>")
parser.add_option("-r", "--raw",
                  action="store_const", const=True, dest="raw",
                  help="output raw response data")

SERVICE_PATH = "/bin/groovyconsole/post.json"


@tool('groovy')
class GroovyTool(object):
    """ http://localhost:4502/bin/groovyconsole/post.json """

    def execute(self, server, argv):
        options, args = parser.parse_args(argv)
        if len(argv) < 2:
            parser.print_help()
            return USER_ERROR

        filename = args[1]

        f = open(filename, 'rb')
        script = f.read()

        form_data = dict(
            script=script
        )
        url = server.url(SERVICE_PATH)
        resp = requests.post(url, auth=server.auth, data=form_data)
        if resp.status_code != 200:
            error("Failed to run script {filename}: {content}".format(
                filename=filename,
                content=resp.content))
            return SERVER_ERROR
        data = resp.json()
        if options.raw:
            sys.stdout.write("{}\n".format(json.dumps(data, indent=4)))
        else:
            # The stacktrace prop changed name with newer versions.
            if data.get('stacktraceText', '') != '':
                sys.stderr.write(data['stacktraceText'])
                return SERVER_ERROR
            elif data['exceptionStackTrace'] != '':
                sys.stderr.write(data['stacktraceText'])
                return SERVER_ERROR
            elif data.get('outputText', '') != '':
                sys.stdout.write("{}".format(data['outputText'].encode('utf-8')))
            else:
                sys.stdout.write("{}".format(data['output'].encode('utf-8')))
        return OK
