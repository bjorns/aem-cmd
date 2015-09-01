# coding: utf-8
""" The wheel binary package format does not support post install
    hooks so we deploy necessary system files here.
"""
import sys
import os.path
import platform

import pkg_resources
import subprocess
import acmd


DEFAULT_COMPLETION_DIR = '/etc/bash_completion.d'
HOMEBREW_COMPLETION_DIR = '/usr/local/etc/bash_completion.d'


def deploy_system_files():
    """ Install any required files for acmd to run well. """
    setup_rcfile(acmd.get_rcfilename())
    deploy_bash_completion()
    if not get_bash_version().startswith("4"):
        acmd.warning("acmd bash completion works better with bash 4.")
        if is_mac():
            acmd.warning("    tip: http://johndjameson.com/blog/updating-your-shell-with-homebrew/")


def read_config_template():
    return pkg_resources.resource_string('acmd', "data/acmd.rc.template")


def setup_rcfile(rcfilename):
    """ Create a new ~/.acmd.rc from template."""
    template = read_config_template()
    if os.path.isfile(rcfilename):
        acmd.warning("Overwriting {}".format(rcfilename))
    target = open(rcfilename, 'wb')
    target.write(template)


def deploy_bash_completion():
    """ Find the bash_completion.d directory and install the packaged script. """
    path = locate_bash_completion_dir()
    if path is not None:
        install_script(path)
    else:
        sys.stderr.write("Could not find bash completion install dir.")


def locate_bash_completion_dir():
    alternatives = [DEFAULT_COMPLETION_DIR, HOMEBREW_COMPLETION_DIR]
    for d in alternatives:
        if os.path.exists(d) and os.path.isdir(d):
            return d
    return None


def install_script(path):
    acmd.log("Installing bash completion to {}".format(path))
    template = pkg_resources.resource_string('acmd', "data/acmd.bash_completion")
    target_path = os.path.join(path, 'acmd')
    if os.path.isfile(target_path):
        acmd.warning("Overwriting bash completion at {}".format(target_path))
    target = open(target_path, 'wb')
    target.write(template)


def get_bash_version():
    try:
        full_text = subprocess.check_output(['bash', '--version'])
        first_line = full_text.split('\n')[0]
        return first_line.lstrip("GNU bash, version ")
    except Exception:
        return "0"

def is_mac():
    return platform.system() == 'Darwin'
