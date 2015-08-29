# encoding: utf-8

# Standard error codes that can be returned from any tool.
USER_ERROR = 4711
CONFIG_ERROR = 4712
SERVER_ERROR = 4713
INTERNAL_ERROR = 4714

import tool_utils
get_command = tool_utils.get_command
get_argument = tool_utils.get_argument

import acmd.tool_repo
acmd.tool_repo.import_tools(__file__, 'acmd.tools')
