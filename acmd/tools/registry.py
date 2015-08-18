# coding: utf-8
_tools = dict()


def register_tool(tool):
    assert get_tool(tool.name) is None
    _tools[tool.name] = tool


def get_tool(tool_name):
    return _tools.get(tool_name)


def list_tools():
    """ Returns list of all tool names."""
    return _tools.keys()
