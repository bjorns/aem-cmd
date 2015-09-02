# coding: utf-8
import sys
import optparse

from acmd import tool
from acmd import OK
from acmd import deploy_bash_completion

parser = optparse.OptionParser("acmd install_bash_completion")


@tool('install_bash_completion')
class InstallBashCompletionTool(object):
    """ Because the wheel binary package format does not permit post-install
        hooks (Platform independence, stop whining.) and is generally not run
        in sudo mode we put this in a separate tool.
    """

    def execute(self, server, argv):
        install_path = deploy_bash_completion()
        sys.stdout.write("Installed bash completion script in {}\n".format(install_path))
        return OK
