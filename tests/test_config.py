# coding: utf-8
from nose.tools import eq_

from acmd.config import read_config


def test_read_config():
    config = read_config('tests/test_data/test_acmd.rc')
    eq_(3, len(config.servers))
    eq_({'extraserver', 'default_server', 'localhost'}, set(config.servers.keys()))
    eq_(config.servers['default_server'], config.servers['extraserver'])
    eq_(None, config.get_server('non existing label'))
    eq_(config.servers['default_server'], config.get_server(None))

    eq_(1, len(config.projects))
    eq_('tests/test_data/fake_project', config.projects['myproj'])
