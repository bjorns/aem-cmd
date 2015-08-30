# coding: utf-8
import os
import sys
import optparse
from os.path import expanduser

import acmd

USAGE = """acmd [options] <tool> <args>
    Run 'acmd help' for list of available tools"""

parser = optparse.OptionParser(USAGE)
parser.add_option("-s", "--server", dest="server",
                  help="server name", metavar="<name>")
parser.add_option("-X", "--verbose",
                  action="store_const", const=True, dest="verbose",
                  help="verbose logging useful for debugging")
parser.add_option("-v", "--version",
                  action="store_const", const=True, dest="show_version",
                  help="Show package version")


def load_projects(projects):
    """ Expecting dict of {<prefix>: <path>} """
    ret = {}
    for name, path in projects.items():
        acmd.log("Loading project {}".format(name))
        path = expanduser(path)
        sys.path.insert(1, path)
        init_file = os.path.join(path, '__init__.py')
        acmd.set_current_project(name)
        acmd.import_tools(init_file)
        ret[name] = path
    return ret


def run(options, args, cmdargs):
    home = expanduser("~")
    rcfilename = "{home}/.acmd.rc".format(home=home)
    if not os.path.isfile(rcfilename):
        acmd.setup_rcfile(rcfilename)
    cfg = acmd.read_config(rcfilename)

    load_projects(cfg.projects)

    tool_name, args = args[1], []
    acmd.init_log(options.verbose)
    server = cfg.get_server(options.server)
    acmd.log("Using server {}".format(server))
    cmd = acmd.get_tool(tool_name)
    if cmd is None:
        sys.stderr.write("error: tool '{cmd}' not found.\n".format(cmd=tool_name))
        return 1
    else:
        return cmd.execute(server, cmdargs)


def split_argv(argv):
    """ Split argument list into system arguments before the tool
    and tool arguments afterwards.
    ['foo', 'bar', 'inspect', 'bink', 'bonk']
        => (['foo', 'bar', 'inspect'], ['inspect', 'bink', 'bonk'])"""
    for i, arg in enumerate(argv):
        if acmd.get_tool(arg) is not None:
            return argv[0:i + 1], argv[i:]
    return argv, []


def main(argv):
    sysargs, cmdargs = split_argv(argv)
    (options, args) = parser.parse_args(sysargs)
    if options.show_version:
        sys.stdout.write("{}\n".format(acmd.__version__))
        sys.exit(0)
    if len(args) <= 1:
        parser.print_help(file=sys.stderr)
        sys.exit(acmd.USER_ERROR)

    status = run(options, args, cmdargs)
    sys.exit(status)
