# coding: utf-8
__version__ = '0.1a7'

import acmd.logger
init_log = acmd.logger.init_log
log = acmd.logger.log
warning = acmd.logger.warning
error = acmd.logger.error


import acmd.server
Server = acmd.server.Server

import acmd.config
read_config = acmd.config.read_config
setup_rcfile = acmd.config.setup_rcfile

import acmd.tool_repo
import_tools = acmd.tool_repo.import_tools
tool = acmd.tool_repo.tool
list_tools = acmd.tool_repo.list_tools
get_tool = acmd.tool_repo.get_tool
register_tool = acmd.tool_repo.register_tool
set_current_project = acmd.tool_repo.set_current_project


# Has to be last if tools init depend on this file.
import acmd.tools
