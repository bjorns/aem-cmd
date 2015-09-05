# coding: utf-8
""" The wheel binary package format does not support post install
    hooks so we deploy necessary system files here.
"""
import sys
import os.path
import platform
import subprocess
from distutils.version import LooseVersion

import pkg_resources

import acmd

DEFAULT_COMPLETION_DIR = '/etc/bash_completion.d'
HOMEBREW_COMPLETION_DIR = '/usr/local/etc/bash_completion.d'


def get_current_version():
    """ Return the version of the currently executing code. """
    return LooseVersion(acmd.__version__)


def setup_rcfile(rcfilename):
    """ Create a new ~/.acmd.rc from template."""
    template = _read_config_template()
    if os.path.isfile(rcfilename):
        acmd.warning("Overwriting {}".format(rcfilename))
    target = open(rcfilename, 'wb')
    target.write(template)


def _read_config_template():
    return pkg_resources.resource_string('acmd', "data/acmd.rc.template")


def deploy_bash_completion(paths=None):
    """ Find the bash_completion.d directory and install the packaged script.
    """
    path = _locate_bash_completion_dir(paths)
    if path is not None:
        acmd.log("Found bash completion script dir {}".format(path))
        install_script(path)
        return path
    else:
        sys.stderr.write("Could not find bash completion install dir.")


def _locate_bash_completion_dir(paths=None):
    """ Bash completion can have many different install directories.
        Find one of them. """
    if paths is None:
        paths = [DEFAULT_COMPLETION_DIR, HOMEBREW_COMPLETION_DIR]
    for path in paths:
        if os.path.exists(path) and os.path.isdir(path):
            return path
    return None


def install_script(path):
    """ Install bash acmd completion script. """
    template = pkg_resources.resource_string('acmd', "data/acmd.bash_completion")
    target_path = os.path.join(path, 'acmd')
    if os.path.isfile(target_path):
        acmd.warning("Overwriting bash completion at {}".format(target_path))
    with open(target_path, 'wb') as target:
        target.write(template)
    if _get_bash_version() < 4:
        acmd.warning("acmd bash completion works better with bash 4.")
        if _is_mac():
            acmd.warning("    tip: http://johndjameson.com/blog/updating-your-shell-with-homebrew/")


def _get_bash_version():
    """ Find version of bash currently running. """
    try:
        full_text = subprocess.check_output(['bash', '--version'])
        first_line = full_text.split('\n')[0]
        version_string = first_line.lstrip("GNU bash, version ")
        major = LooseVersion(version_string).version[0]
        return major
    except Exception as e:
        acmd.log("No bash was found: " + e.message)
        return 0


def _is_mac():
    """ Return True if process is running on a mac. """
    return platform.system() == 'Darwin'
