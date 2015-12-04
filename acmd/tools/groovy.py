# coding: utf-8
import json
import optparse
import sys

from acmd import tool, error
from acmd import OK, USER_ERROR, SERVER_ERROR, INTERNAL_ERROR
from acmd import backend

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
        f = open(filename, 'r')
        status, data = backend.execute(server, f.read(), [], raw_output=options.raw)

        if status != OK:
            error("Failed to run script {filename}: {content}".format(
                filename=filename,
                content=data))
            return SERVER_ERROR

        if options.raw:
            sys.stdout.write("{}\n".format(json.dumps(data, indent=4)))
        else:
            # The stacktrace prop changed name with newer versions.
            if backend.STACKTRACE_FIELD in data:
                sys.stderr.write(data[backend.STACKTRACE_FIELD])
                return SERVER_ERROR
            elif backend.OUTPUT_FIELD in data:
                sys.stdout.write("{}".format(data[backend.OUTPUT_FIELD].encode('utf-8')))
            else:
                return INTERNAL_ERROR
        return OK

    def build_form_data(self, filename):
        f = open(filename, 'rb')
        form_data = dict(
            script=replace_vars(f.read())
        )
        return form_data


def replace_vars(content):
    return content
