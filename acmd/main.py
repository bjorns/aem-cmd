# coding: utf-8
import os
import os.path
import sys
import optparse

import acmd
import acmd.tools

USAGE = """acmd [options] <tool> <args>
    Run 'acmd help' for list of available tools"""

parser = optparse.OptionParser(USAGE)
parser.add_option("-s", "--server", dest="server",
                  help="server name", metavar="<name>")
parser.add_option("-v", "--verbose",
                  action="store_const", const=True, dest="verbose",
                  help="verbose logging useful for debugging")
parser.add_option("-V", "--version",
                  action="store_const", const=True, dest="show_version",
                  help="Show package version")


def run(options, config, args, cmdargs):
    tool_name, args = args[1], []
    server = config.get_server(options.server)
    if server is None:
        sys.stderr.write("error: server '{srv}' not found.\n".format(srv=options.server))
        return acmd.USER_ERROR
    acmd.log("Using server {}".format(server))

    _tool = acmd.tool_repo.get_tool(tool_name)
    _tool.config = config

    if _tool is None:
        sys.stderr.write("error: tool '{cmd}' not found.\n".format(cmd=tool_name))
        return acmd.USER_ERROR
    else:
        status = _tool.execute(server, cmdargs)
        if status is None:
            raise Exception("Unexpected error, tool {} should return valid status code".format(tool_name))
        return status


def split_argv(argv):
    """ Split argument list into system arguments before the tool
        and tool arguments afterwards.
        ['foo', 'bar', 'inspect', 'bink', 'bonk']
            => (['foo', 'bar', 'inspect'], ['inspect', 'bink', 'bonk'])"""
    acmd.log("Splitting {}".format(argv))
    for i, arg in enumerate(argv):
        acmd.log("Checking for {}".format(arg))
        if acmd.tool_repo.has_tool(arg):
            left = argv[0:i + 1]
            right = argv[i:]
            acmd.log("Splitting args in {} and {}".format(left, right))
            return left, right
    return argv, []


def main(argv, rcfile=None):
    if not rcfile:
        rcfile = acmd.get_rcfilename()
    if not os.path.isfile(rcfile):
        acmd.setup_rcfile(rcfile)
    config = acmd.read_config(rcfile)
    acmd.tools.init_default_tools(config)
    acmd.import_projects(config.projects)

    sysargs, cmdargs = split_argv(argv)

    (options, args) = parser.parse_args(sysargs)
    acmd.init_log(options.verbose)

    if options.show_version:
        sys.stdout.write("{}\n".format(acmd.__version__))
        sys.exit(0)
    if len(args) <= 1:
        parser.print_help(file=sys.stderr)
        sys.exit(acmd.USER_ERROR)

    status = run(options, config, args, cmdargs)
    sys.exit(status)
