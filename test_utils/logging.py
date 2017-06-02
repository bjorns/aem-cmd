# coding: utf-8

LOG = open('tests.log', 'a')


def test_log(msg):
    LOG.write("{}\n".format(msg))
