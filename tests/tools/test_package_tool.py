# coding: utf-8
from httmock import urlmatch, HTTMock
from mock import patch
from nose.tools import eq_

from acmd import tool_repo, Server, USER_ERROR
from acmd.tools.package_tool import PackageTool

from test_utils.compat import StringIO


def test_tool_registration():
    tool = tool_repo.get_tool('package')
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


EXPECTED_LIST = [["test_packages", "mock_package", "1.6.5", "Fri, 13 Jun 2014 14:16:31 -0400"],
                 ["adobe/granite", "com.adobe.coralui.rte-cq5", "5.6.18", "Fri, 13 Jun 2014 14:18:11 -0400"],
                 ["adobe/granite", "com.adobe.granite.activitystreams.content", "0.0.12",
                  "Fri, 13 Jun 2014 14:16:32 -0400"]]


def untab(data):
    lines = data.split("\n")
    return list(map(lambda x: x.split('\t'), lines))


@patch('sys.stdout', new_callable=StringIO)
def test_list_packages(stdout):
    with HTTMock(packages_mock):
        tool = PackageTool()
        server = Server('localhost')

        tool.execute(server, ['package', 'list'])

        i = 0
        for line in EXPECTED_LIST:
            eq_(line, untab(stdout.getvalue())[i])
            i += 1


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_upload_package(stderr, stdout):
    with HTTMock(upload_packages_mock):
        tool = PackageTool()
        server = Server('localhost')

        status = tool.execute(server, ['package', 'upload', 'tests/test_data/mock_package.zip'])
        eq_(0, status)
        eq_(["my_packages", "mock-package", "1.0", "Tue, 29 Sep 2015 16:20:59 -0400"], untab(stdout.getvalue())[0])
        eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_upload_package_raw(stderr, stdout):
    with HTTMock(upload_packages_mock):
        tool = PackageTool()
        server = Server('localhost')

        status = tool.execute(server, ['package', 'upload', '--raw', 'tests/test_data/mock_package.zip'])
        eq_(0, status)
        eq_('', stderr.getvalue())
        eq_(True, len(stdout.getvalue()) > 0)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_upload_package_and_install(stderr, stdout):
    with HTTMock(upload_packages_mock):
        tool = PackageTool()
        server = Server('localhost')

        status = tool.execute(server, ['package', 'upload', '--install', 'tests/test_data/mock_package.zip'])
        eq_(0, status)
        eq_('', stderr.getvalue())
        eq_(True, len(stdout.getvalue()) > 0)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_install_package(stderr, stdout):
    with HTTMock(packages_mock):
        tool = PackageTool()
        server = Server('localhost')

        status = tool.execute(server, ['package', 'install', 'mock_package'])
        eq_(0, status)
        eq_('Package Installed\n', stdout.getvalue())
        eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_uninstall_package(stderr, stdout):
    with HTTMock(packages_mock):
        tool = PackageTool()
        server = Server('localhost')

        status = tool.execute(server, ['package', 'uninstall', 'mock_package'])
        eq_(0, status)
        eq_('', stdout.getvalue())
        eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_install_package_raw(stderr, stdout):
    with HTTMock(packages_mock):
        tool = PackageTool()
        server = Server('localhost')

        status = tool.execute(server, ['package', 'install', '--raw', 'mock_package'])
        eq_(0, status)
        eq_('{"success": true, "msg": "Package Installed"}\n', stdout.getvalue())
        eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_build_package(stderr, stdout):
    with HTTMock(packages_mock):
        tool = tool_repo.get_tool('package')
        server = Server('localhost')
        status = tool.execute(server, ['package', 'build', 'mock_package'])
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
        tool = tool_repo.get_tool('package')
        server = Server('localhost')
        status = tool.execute(server, ['package', 'download', 'mock_package'])
    eq_(0, status)
    eq_('mock_package-1.6.5.zip\n', stdout.getvalue())
    eq_('', stderr.getvalue())
    url, request = get_command_stack()[-1]
    eq_('/etc/packages/test_packages/mock_package-1.6.5.zip', url.path)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_bad_command(*_):
    tool = tool_repo.get_tool('package')
    server = Server('localhost')
    status = tool.execute(server, ['package', 'nonexisting', 'mock_package'])
    eq_(USER_ERROR, status)
