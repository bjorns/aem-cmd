# coding: utf-8
from nose.tools import eq_
from nose.tools import raises

from acmd.util.html import split, parse_value


def test_split():
    key, val = split("name=Joe")
    eq_('name', key)
    eq_('Joe', val)


def test_split_single():
    key, val = split("foobar")
    eq_('id', key)
    eq_('foobar', val)


INPUT = """
<html>
    <value id="foobar">Expected value</value>
</html>
"""


def test_parse_value():
    x = parse_value(INPUT, 'value', 'id=foobar')
    eq_('Expected value', x)


def test_parse_value_anon():
    x = parse_value(INPUT, 'value', 'foobar')
    eq_('Expected value', x)


@raises(Exception)
def test_parse_value_missing_attr_key():
    parse_value(INPUT, 'value', 'notexist=foobar')


@raises(Exception)
def test_parse_value_missing_attr_value():
    parse_value(INPUT, 'value', 'id=nonexist')


@raises(Exception)
def test_parse_value_missing_entity():
    parse_value(INPUT, 'nonexist', 'id=nonexist')
