# coding: utf-8
from nose.tools import eq_

from acmd.util.strings import remove_prefix, remove_suffix


def test_remove_prefix():
    eq_("bar", remove_prefix("foo", "foobar"))


def test_remove_suffix():
    eq_("foo", remove_suffix("bar", "foobar"))
    eq_("fooba", remove_suffix("r", "foobar"))
