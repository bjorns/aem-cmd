# encoding: utf-8

import tool_utils
get_command = tool_utils.get_action
get_argument = tool_utils.get_argument

import acmd.tool_repo
acmd.tool_repo.import_tools(__file__, 'acmd.tools')
