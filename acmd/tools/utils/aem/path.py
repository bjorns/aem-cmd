# coding: utf-8


def join(path, *paths):
    """ Connect two aem paths. Should have same function as os.path.join
        but not be affected by windows """
    ret = path;
    for p in paths:
        ret = _join_two(ret, p)
    return ret


def _join_two(path0, path1):
    if path0.endswith("/"):
        path0 = path0[:-1]
    if path1.startswith("/"):
        path1 = path1[1:]
    return "{}/{}".format(path0, path1)
