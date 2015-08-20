# coding: utf-8

def get_action(argv, default):
    if len(argv) < 2:
        return default
    else:
        return argv[1]
