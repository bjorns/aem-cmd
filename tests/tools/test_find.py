# coding: utf-8
from mock import patch
from httmock import urlmatch, HTTMock
from nose.tools import eq_

from acmd import tool_repo, Server

from test_utils.console import unordered_list
from test_utils.compat import StringIO

CONTENT_RESPONSE = """{
    "jcr:primaryType": "nt:folder",
    "path": {
        "jcr:primaryType": "sling:Folder",
        "jcr:created": "Wed Mar 04 2015 04:56:30 GMT-0500",
        "jcr:createdBy": "admin"
    }
}"""

DIR_RESPONSE = """{
    "jcr:primaryType": "nt:folder"
}"""

PATH_RESPONSE = """{
    "jcr:mixinTypes": [
        "rep:AccessControllable",
        "cq:ReplicationStatus"
    ],
    "jcr:primaryType": "nt:folder",
    "cq:lastReplicatedBy": "admin",
    "jcr:created": "Fri Jul 25 2014 11:38:40 GMT-0400",
    "cq:lastReplicationAction": "Activate",
    "jcr:createdBy": "admin",
    "cq:lastReplicated": "Tue Aug 25 2015 20:21:20 GMT-0400",
    "directory": {
        "jcr:primaryType": "sling:Folder",
        "jcr:created": "Wed Mar 04 2015 04:56:30 GMT-0500",
        "jcr:createdBy": "admin"
    },
    "node": {
        "title": "Test Title",
        "text": "Something something",
        "jcr:primaryType": "nt:unstructured"
    }
}"""

NODE_RESPONSE = """{
    "title": "Test Title",
    "text": "Something something",
    "jcr:primaryType": "nt:unstructured"
}"""


@urlmatch(netloc='localhost:4502', method='GET')
def service_mock(url, _):
    if url.path == '/content.1.json':
        return CONTENT_RESPONSE
    elif url.path == '/content/path.1.json':
        return PATH_RESPONSE
    elif url.path == '/content/path/directory.1.json':
        return DIR_RESPONSE
    elif url.path == '/content/path/node.1.json':
        return NODE_RESPONSE
    else:
        raise Exception(url.path)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_find(stderr, stdout):
    with HTTMock(service_mock):
        tool = tool_repo.get_tool('find')
        server = Server('localhost')
        status = tool.execute(server, ['find', '/content'])
        eq_(0, status)
        eq_({'/content', '/content/path', '/content/path/node', '/content/path/directory'},
            unordered_list(stdout.getvalue()))
        eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
@patch('sys.stdin', new=StringIO('/content\n'))
def test_find_stdin(stderr, stdout):
    with HTTMock(service_mock):
        tool = tool_repo.get_tool('find')
        server = Server('localhost')
        status = tool.execute(server, ['find'])
        eq_(0, status)
        eq_({'/content', '/content/path', '/content/path/node', '/content/path/directory'},
            unordered_list(stdout.getvalue()))
        eq_('', stderr.getvalue())
