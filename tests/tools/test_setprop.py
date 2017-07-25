# coding: utf-8
from httmock import urlmatch, HTTMock
from mock import patch
from nose.tools import eq_

from acmd import tool_repo, Server
from acmd.util.props import parse_properties, format_multipart

from test_utils.compat import StringIO


class MockHttpService(object):
    def __init__(self, asset_service=None):
        self.req_log = []
        self.asset_service = asset_service

    @urlmatch(netloc='localhost:4502')
    def __call__(self, url, request):
        self.req_log.append(request)
        return ""


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

    x = 'ary=[foo,bar,baz]'
    props = parse_properties(x)
    eq_(2, len(props))
    eq_(['foo', 'bar', 'baz'], props['ary'])
    eq_('String[]', props['ary@TypeHint'])


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_setprop(_, stdout):
    service_mock = MockHttpService()
    with HTTMock(service_mock):
        tool = tool_repo.get_tool('setprop')
        server = Server('localhost')
        status = tool.execute(server, ['setprop', 'prop0=value0,prop1=value1', '/content/path/node'])
        eq_(0, status)
        eq_('/content/path/node\n', stdout.getvalue())
    eq_(1, len(service_mock.req_log))
    eq_({('prop1', 'value1'), ('prop0', 'value0')}, set(service_mock.req_log[0].body.fields))


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
@patch('sys.stdin', new=StringIO("/path0\n/path1\n"))
def test_setprop_stdin(_, stdout):
    service_mock = MockHttpService()
    with HTTMock(service_mock):
        tool = tool_repo.get_tool('setprop')
        server = Server('localhost')
        status = tool.execute(server, ['setprop', 'prop0=value0,prop1=value1'])
        eq_(0, status)
        eq_('/path0\n/path1\n', stdout.getvalue())
    eq_(2, len(service_mock.req_log))
    eq_({('prop1', 'value1'), ('prop0', 'value0')}, set(service_mock.req_log[0].body.fields))


def test_flatten():
    item0 = ('one', 1)
    item1 = ('two', 2)
    eq_({item1, item0}, set(format_multipart(dict(one=1, two=2))))

    eq_((('array', 1), ('array', 2), ('array', 3)), format_multipart(dict(array=[1, 2, 3])))
