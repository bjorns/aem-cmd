# coding: utf-8
import os
import sys

from acmd.logger import log
from acmd.tools import init_default_tools


class ToolRepo(object):
    def __init__(self):
        self._tools = dict()
        self._modules = dict()
        # This is a hack, couldn't come up with a nice way of setting the
        # tool prefix automatically.
        self._init_project = None

    def register_tool(self, _tool, _module):
        assert _tool.name not in self._tools
        if self._init_project is None:
            name = _tool.name
        else:
            name = self._init_project + ':' + _tool.name
        log("Registering tool {}".format(name))
        self._tools[name] = _tool
        self._modules[name] = _module

    def get_tool(self, tool_name):
        ret = self._tools.get(tool_name)
        if ret is None:
            raise Exception("Tool {} is missing".format(tool_name))
        return ret

    def has_tool(self, tool_name):
        ret = self._tools.get(tool_name)
        return ret is not None

    def get_module(self, tool_name):
        return self._modules[tool_name]

    def list_tools(self):
        tool_names = self._tools.keys()
        tool_names.sort()
        return tool_names

    def set_current_project(self, name):
        self._init_project = name

# Global singleton, no use in passing the thing around
tool_repo = ToolRepo()


def tool(tool_name, commands=None):
    """ Tool decorator.

        Creates an instance and instantiates
        it so the user does not have to write boilerplate.

        Usage: Decorate your class with @tool(<tool_name>) e.g.

        @tool('packages')
    """

    def class_rebuilder(cls):
        global tool_repo
        instance = cls()

        instance.name = tool_name
        if not hasattr(instance, 'commands'):
            instance.commands = commands if commands is not None else []
        _module = __import__(cls.__module__, locals(), globals(), '__main__', 0)

        tool_repo.register_tool(instance, _module)
        return cls

    return class_rebuilder


def import_tools(path, package=None):
    module = None
    try:
        modules = os.listdir(os.path.dirname(path))
    except OSError:
        sys.stderr.write("error: Failed to load modules in {}".format(path))
        modules = []
        pass
    for module in modules:
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        if package is not None:
            __import__(package, locals(), globals(), [module[:-3]], 0)
        else:
            __import__(module[:-3], locals(), globals())
    del module
