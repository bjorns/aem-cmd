# coding: utf-8
import os
from acmd import log

_tools = dict()


def tool(tool_name, commands=None):
    """ Tool decorator.

        Creates an instance and instantiates
        it so the user does not have to write boilerplate.

        Usage: Decorate your class with @tool(<tool_name>) e.g.

        @tool('packages')
        """

    def class_rebuilder(cls):
        instance = cls()
        instance.name = tool_name
        if not hasattr(instance, 'commands'):
            instance.commands = commands if commands is not None else []
        register_tool(instance)
        return cls

    return class_rebuilder


def import_tools(path, package=None):
    module = None
    for module in os.listdir(os.path.dirname(path)):
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        if package is not None:
            __import__(package, locals(), globals(), [module[:-3]], 0)
        else:
            __import__(module[:-3], locals(), globals())
    del module


# This is a hack, couldn't come up with a nice way of setting the
# tool prefix automatically.
_init_project = None
def set_current_project(name):
    """ Set a project name context when initializing project tools. """
    global _init_project
    _init_project = name

def register_tool(_tool):
    assert get_tool(_tool.name) is None
    if _init_project is None:
        name = _tool.name
    else:
        name = _init_project + ':' + _tool.name
    log("Registering tool {}".format(name))
    _tools[name] = _tool


def get_tool(tool_name):
    return _tools.get(tool_name)


def list_tools():
    """ Returns list of all tool names."""
    tool_names = _tools.keys()
    tool_names.sort()
    return tool_names
