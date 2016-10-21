# coding: utf-8
import random
import string


def get_command(argv, default=None):
    if len(argv) < 2:
        return default
    else:
        return argv[1]


def get_argument(argv, i=2, default=""):
    if len(argv) < i + 1:
        return default
    else:
        return argv[i]


def filter_system(items):
    """ Filter properties that start with jcr: """
    f = lambda (key, data): not key.startswith('jcr:')
    return filter(f, items)


def random_hex(num_chars):
    lst = [random.choice("abcdef" + string.digits) for _ in xrange(num_chars)]
    return ''.join(lst)


def create_task_id(prefix):
    return "{prefix}-{id}".format(prefix=prefix, id=random_hex(6))
