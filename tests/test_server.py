# coding: utf-8
import acmd
from nose.tools import eq_

def test_default_values():
    s = acmd.Server('foobar')
    assert s.name == 'foobar'
    assert s.host == 'localhost'
    assert s.port == 4502
    assert s.username == 'admin'
    assert s.password == 'admin'


def test_constructor():
    s = acmd.Server('foobar', host='sb3.com', port=4711,
        username='bjorn', password='foobar')
    assert s.name == 'foobar'
    assert s.host == 'sb3.com'
    assert s.port == 4711
    assert s.username == 'bjorn'
    assert s.password == 'foobar'
    eq_(('bjorn', 'foobar'), s.auth)

def test_url():
    s = acmd.Server('foobar')

    eq_('http://localhost:4502/local/path', s.url('/local/path'))
