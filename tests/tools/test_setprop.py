# coding: utf-8
from StringIO import StringIO

from httmock import urlmatch, HTTMock
from mock import patch
from nose.tools import eq_

from acmd import tool_repo, Server
from acmd.tools.jcr import parse_properties, _flatten


def test_parser_properties():
    x = 'key=value'
    props = parse_properties(x)
    eq_(1, len(props))
    eq_('value', props['key'])

    x = 'key0=value0,key1=value1'
    props = parse_properties(x)
    eq_(2, len(props))
    eq_('value0', props['key0'])
    eq_('value1', props['key1'])

    x = 'key0="value0",key1="value1"'
    props = parse_properties(x)
    eq_('value0', props['key0'])
    eq_('String', props['key0@TypeHint'])
    eq_('value1', props['key1'])
    eq_('String', props['key1@TypeHint'])
    eq_(4, len(props))

    x = 'key0="value0",key1="Sentence with \\"quotes in it\\""'
    props = parse_properties(x)

    eq_(4, len(props))
    eq_('value0', props['key0'])
    eq_('String', props['key0@TypeHint'])
    eq_('Sentence with \\"quotes in it\\"', props['key1'])
    eq_('String', props['key1@TypeHint'])

    x = 'key0="value0",key1="Sentence, with comma in it"'
    props = parse_properties(x)
    eq_(4, len(props))
    eq_('value0', props['key0'])
    eq_('String', props['key0@TypeHint'])
    eq_('Sentence, with comma in it', props['key1'])
    eq_('String', props['key1@TypeHint'])


@urlmatch(netloc='localhost:4502', method='POST')
def service_mock(url, request):
    eq_('prop0=value0&prop1=value1', request.body)
    return ""


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_setprop(stderr, stdout):
    with HTTMock(service_mock):
        tool = tool_repo.get_tool('setprop')
        server = Server('localhost')
        status = tool.execute(server, ['setprop', 'prop0=value0,prop1=value1', '/content/path/node'])
        eq_(0, status)
        eq_('/content/path/node\n', stdout.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
@patch('sys.stdin', new=StringIO("/path0\n/path1\n"))
def test_setprop_stdin(stderr, stdout):
    with HTTMock(service_mock):
        tool = tool_repo.get_tool('setprop')
        server = Server('localhost')
        status = tool.execute(server, ['setprop', 'prop0=value0,prop1=value1'])
        eq_(0, status)
        eq_('/path0\n/path1\n', stdout.getvalue())


def test_flatten():
    item0 = ('one', 1)
    item1 = ('two', 2)
    eq_((item1, item0), _flatten(dict(one=1, two=2)))

    eq_((('array', 1), ('array', 2), ('array', 3)), _flatten(dict(array=[1, 2, 3])))
