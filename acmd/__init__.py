# coding: utf-8
""" aem-cmd main module. """
import acmd.logger
import acmd.server
import acmd.config
import acmd.deploy
import acmd.repo

__version__ = '0.14.6b'

# Standard error codes that can be returned from any tool.
OK = 0
UNCHANGED = 1
USER_ERROR = 4711
CONFIG_ERROR = 4712
SERVER_ERROR = 4713
INTERNAL_ERROR = 4714


# Make key modules available in root namespace

# Logging
init_log = acmd.logger.init_log
log = acmd.logger.log
warning = acmd.logger.warning
error = acmd.logger.error

# Server config
Server = acmd.server.Server

# Config
read_config = acmd.config.read_config
get_rcfilename = acmd.config.get_rcfilename

setup_rcfile = acmd.deploy.setup_rcfile
deploy_bash_completion = acmd.deploy.deploy_bash_completion

# Version introspection
get_current_version = acmd.deploy.get_current_version

# Tool Interface
tool_repo = acmd.repo.tool_repo
tool = acmd.repo.tool
import_projects = acmd.repo.import_projects
