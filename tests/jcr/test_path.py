from nose.tools import eq_

from acmd.jcr.path import join


def test_simple_join():
    eq_("/content/dam", join("/content/", "/dam"))
    eq_("/content/dam", join("/content", "/dam"))
    eq_("/content/dam", join("/content/", "dam"))
    eq_("/content/dam", join("/content", "dam"))


def test_vararg_join():
    eq_("/content/dam/test/foobar", join("/content", "dam", "test", "/foobar"))
