# coding: utf-8
import os
import sys
from os.path import expanduser

import acmd


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


def main(options, args, cmdargs):
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
