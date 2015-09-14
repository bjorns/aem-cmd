# coding: utf-8


def get_action(argv, default=None):
    if len(argv) < 2:
        return default
    else:
        return argv[1]


def get_argument(argv, i=2, default=None):
    if len(argv) < i+1:
        return default
    else:
        return argv[i]


def filter_system(items):
    f = lambda (key, data): not key.startswith('jcr:')
    return filter(f, items)
