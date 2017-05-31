# coding: utf-8


def unordered_list(data):
    ret = set(data.split("\n"))
    ret.remove('')
    return ret

