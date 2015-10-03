# coding: utf-8
__version__ = '0.6b1'

# Standard error codes that can be returned from any tool.
OK = 0
USER_ERROR = 4711
CONFIG_ERROR = 4712
SERVER_ERROR = 4713
INTERNAL_ERROR = 4714


import acmd.logger
init_log = acmd.logger.init_log
log = acmd.logger.log
warning = acmd.logger.warning
error = acmd.logger.error


import acmd.server
Server = acmd.server.Server

import acmd.config
read_config = acmd.config.read_config
get_current_config = acmd.config.get_current_config
get_rcfilename = acmd.config.get_rcfilename

import acmd.deploy
setup_rcfile = acmd.deploy.setup_rcfile
deploy_bash_completion = acmd.deploy.deploy_bash_completion

get_current_version = acmd.deploy.get_current_version

import acmd.props
parse_properties = acmd.props.parse_properties


import acmd.tool_repo
import_tools = acmd.tool_repo.import_tools
tool = acmd.tool_repo.tool
list_tools = acmd.tool_repo.list_tools
get_tool = acmd.tool_repo.get_tool
register_tool = acmd.tool_repo.register_tool
set_current_project = acmd.tool_repo.set_current_project


# Has to be last if tools init depend on this file.
import acmd.tools
