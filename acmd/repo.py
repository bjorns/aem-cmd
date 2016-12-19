# coding: utf-8
import os
import sys
import importlib

from acmd.logger import log


class ToolRepo(object):
    def __init__(self):
        self._tools = dict()
        self._modules = dict()
        # This is a hack, couldn't come up with a nice way of setting the
        # tool prefix automatically.
        self._init_project = None

    def reset(self):
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
        return tool_name in self._tools

    def get_module(self, tool_name):
        return self._modules[tool_name]

    def list_tools(self):
        tool_names = self._tools.keys()
        tool_names.sort()
        return tool_names

    def set_prefix(self, name):
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


def _list_files(path):
    try:
        return os.listdir(os.path.dirname(path))
    except OSError:
        sys.stderr.write("error: Failed to load modules in {}".format(path))
        return []


def import_tools(path, package=None, prefix=None):
    log("Importing path {} : {}\n".format(path, package))
    pyfiles = _list_files(path)

    tool_repo.set_prefix(prefix)
    for pyfile in pyfiles:
        if pyfile == '__init__.py' or pyfile[-3:] != '.py':
            continue

        module = pyfile[:-3]
        if package is not None:
            module = "{}.{}".format(package, module)

        log("  Importing module {}\n".format(module))
        importlib.import_module(module)
