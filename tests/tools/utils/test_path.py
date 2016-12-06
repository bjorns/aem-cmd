from nose.tools import eq_

from acmd.tools.utils import aem


def test_simple_join():
    eq_("/content/dam", aem.path.join("/content/", "/dam"))
    eq_("/content/dam", aem.path.join("/content", "/dam"))
    eq_("/content/dam", aem.path.join("/content/", "dam"))
    eq_("/content/dam", aem.path.join("/content", "dam"))


def test_vararg_join():
    eq_("/content/dam/test/foobar", aem.path.join("/content", "dam", "test", "/foobar"))
