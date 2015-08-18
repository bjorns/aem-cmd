# coding: utf-8
from acmd.tools.registry import register_tool

def tool(tool_name):
    """ Tool decorator.

        Creates an instance and instantiates
        it so the user does not have to write boilerplate.

        Usage: Decorate your class with @tool(<tool_name>) e.g.

        @tool('packages')
        """
    def class_rebuilder(cls):
        instance = cls()
        instance.name = tool_name
        register_tool(instance)
        return cls

    return class_rebuilder

