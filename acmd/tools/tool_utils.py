# coding: utf-8

def get_command(argv, default):
    if len(argv) < 2:
        return default
    else:
        return argv[1]


def get_argument(argv):
    if len(argv) < 3:
        return None
    else:
        return argv[2]

