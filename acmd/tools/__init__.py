# encoding: utf-8

import tool_utils
get_command = tool_utils.get_command
get_argument = tool_utils.get_argument
filter_system = tool_utils.filter_system


import acmd.tool_repo
acmd.tool_repo.import_tools(__file__, 'acmd.tools')
