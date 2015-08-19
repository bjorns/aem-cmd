# coding: utf-8
import acmd.server
import acmd.config
import acmd.tools.registry

read_config = acmd.config.read_config

get_tool = acmd.tools.registry.get_tool
register_tool = acmd.tools.registry.register_tool

Server = acmd.server.Server
