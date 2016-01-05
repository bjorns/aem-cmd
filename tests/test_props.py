# coding: utf-8
from acmd import parse_properties

from nose.tools import eq_


def test_parse_simple_prop():
    y = parse_properties("foobar=baz")
    eq_(1, len(y))
    eq_('baz', y['foobar'])


def test_parse_quoted_prop():
    y = parse_properties("name=\"John Doe\"")
    eq_(2, len(y))
    eq_('John Doe', y['name'])
    eq_('String', y['name@TypeHint'])


def test_parse_double_quoted_prop():
    y = parse_properties('name="John \\"The machine\\" Doe"')
    eq_(2, len(y))
    eq_('John \\"The machine\\" Doe', y['name'])
    eq_('String', y['name@TypeHint'])


def test_parse_multi_props():
    y = parse_properties("first=John,last=Doe")
    eq_(2, len(y))
    eq_('John', y['first'])
    eq_('Doe', y['last'])


def test_parse_boolean():
    y = parse_properties("should_work=true")
    eq_(2, len(y))
    eq_('true', y['should_work'])
    eq_('Boolean', y['should_work@TypeHint'])


def test_parse_integer():
    y = parse_properties("nbr_dwarves=7")
    eq_(2, len(y))
    eq_('7', y['nbr_dwarves'])
    eq_('Long', y['nbr_dwarves@TypeHint'])


def test_parse_quoted_number():
    y = parse_properties("answer=\"42\"")
    eq_(2, len(y))
    eq_('42', y['answer'])
    eq_('String', y['answer@TypeHint'])

