# coding: utf-8
import random
import string


def get_action(argv, default=None):
    """ Get the tool action part of the argument list """
    if len(argv) < 2:
        return default
    else:
        return argv[1]


def get_argument(argv, i=2, default=""):
    """ Get the tool argument part of the argument list """
    if len(argv) < i + 1:
        return default
    else:
        return argv[i]


def filter_system(dict_data):
    """ Filter properties that start with jcr:
        :return pair iterator
    """
    # ret = filter(lambda key, data: not key.startswith('jcr:'), items)
    ret = {key: data for key, data in dict_data.items() if not key.startswith('jcr:')}
    return ret.items()


def random_hex(num_chars):
    """ Generate random hexadecimal string """
    lst = [random.choice("abcdef" + string.digits) for _ in range(num_chars)]
    return ''.join(lst)


def create_task_id(prefix):
    """ Create random task-id """
    return "{prefix}-{id}".format(prefix=prefix, id=random_hex(6))
