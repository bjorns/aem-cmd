# encoding: utf-8

import tool_utils
import acmd.repo

get_command = tool_utils.get_command
get_argument = tool_utils.get_argument
filter_system = tool_utils.filter_system


def init_default_tools():
    acmd.repo.import_tools(__file__, 'acmd.tools', prefix=None)
