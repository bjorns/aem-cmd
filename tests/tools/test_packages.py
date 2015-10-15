# coding: utf-8
from StringIO import StringIO

from mock import patch
from httmock import urlmatch, HTTMock
from nose.tools import eq_

from acmd.tools import packages
from acmd import get_tool, Server, USER_ERROR


def test_tool_registration():
    tool = get_tool('packages')
    assert tool is not None


_command_stack = []
def get_command_stack():
    global _command_stack
    return _command_stack

@urlmatch(netloc='localhost:4502')
def packages_mock(url, request):
    get_command_stack().append((url, request))

    if request.method == 'POST':
        if url.path == '/crx/packmgr/service.jsp':
            with open('tests/test_data/packages_list.xml') as f:
                return f.read()
        elif url.path.startswith('/crx/packmgr/service/.json/etc/packages'):
            return '{"success": true, "msg": "Package Installed"}'
        else:
            raise Exception("Unknown path " + url.path)
    elif request.method == 'GET':
        if url.path == '/etc/packages/test_packages/mock_package-1.6.5.zip':
            return '{"success":true,"msg":"Package built"}'

    else:
        raise Exception("Unknown method " + request.method + " for " + url.path)


@urlmatch(netloc='localhost:4502')
def upload_packages_mock(url, request):
    get_command_stack().append((url, request))

    if request.method == 'POST':
        if url.path == '/crx/packmgr/service.jsp':
            with open('tests/test_data/package_upload_response.xml') as f:
                return f.read()
    raise Exception("Unknown method " + request.method)

EXPECTED_LIST = """test_packages\tmock_package\t1.6.5
adobe/granite\tcom.adobe.coralui.rte-cq5\t5.6.18
adobe/granite\tcom.adobe.granite.activitystreams.content\t0.0.12
"""


@patch('sys.stdout', new_callable=StringIO)
def test_list_packages(stdout):
    with HTTMock(packages_mock):
        tool = packages.PackagesTool()
        server = Server('localhost')

        tool.execute(server, ['packages', 'list'])
        eq_(EXPECTED_LIST, stdout.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_upload_package(stderr, stdout):
    with HTTMock(upload_packages_mock):
        tool = packages.PackagesTool()
        server = Server('localhost')

        status = tool.execute(server, ['packages', 'upload', 'tests/test_data/mock_package.zip'])
        eq_(0, status)
        eq_('my_packages\tmock-package\t1.0\n', stdout.getvalue())
        eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_upload_package_raw(stderr, stdout):
    with HTTMock(upload_packages_mock):
        tool = packages.PackagesTool()
        server = Server('localhost')

        status = tool.execute(server, ['packages', 'upload', '--raw', 'tests/test_data/mock_package.zip'])
        eq_(0, status)
        eq_('', stderr.getvalue())
        eq_(True, len(stdout.getvalue()) > 0)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_upload_package_and_install(stderr, stdout):
    with HTTMock(upload_packages_mock):
        tool = packages.PackagesTool()
        server = Server('localhost')

        status = tool.execute(server, ['packages', 'upload', '--install', 'tests/test_data/mock_package.zip'])
        eq_(0, status)
        eq_('', stderr.getvalue())
        eq_(True, len(stdout.getvalue()) > 0)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_install_package(stderr, stdout):
    with HTTMock(packages_mock):
        tool = packages.PackagesTool()
        server = Server('localhost')

        status = tool.execute(server, ['packages', 'install', 'mock_package'])
        eq_(0, status)
        eq_('Package Installed\n', stdout.getvalue())
        eq_('', stderr.getvalue())

@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_install_package_raw(stderr, stdout):
    with HTTMock(packages_mock):
        tool = packages.PackagesTool()
        server = Server('localhost')

        status = tool.execute(server, ['packages', 'install', '--raw', 'mock_package'])
        eq_(0, status)
        eq_('{"success": true, "msg": "Package Installed"}\n', stdout.getvalue())
        eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_build_package(stderr, stdout):
    with HTTMock(packages_mock):
        tool = get_tool('packages')
        server = Server('localhost')
        status = tool.execute(server, ['packages', 'build', 'mock_package'])
        eq_(0, status)
        eq_('', stdout.getvalue())
        eq_('', stderr.getvalue())
        url, request = get_command_stack()[-1]
        eq_('/crx/packmgr/service/.json/etc/packages/test_packages/mock_package-1.6.5.zip', url.path)
        eq_('cmd=build', request.body)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_download(stderr, stdout):
    with HTTMock(packages_mock):
        tool = get_tool('packages')
        server = Server('localhost')
        status = tool.execute(server, ['packages', 'download', 'mock_package'])
    eq_(0, status)
    eq_('mock_package-1.6.5.zip\n', stdout.getvalue())
    eq_('', stderr.getvalue())
    url, request = get_command_stack()[-1]
    eq_('/etc/packages/test_packages/mock_package-1.6.5.zip', url.path)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_bad_command(stderr, stdout):
    tool = get_tool('packages')
    server = Server('localhost')
    status = tool.execute(server, ['packages', 'nonexisting', 'mock_package'])
    eq_(USER_ERROR, status)
