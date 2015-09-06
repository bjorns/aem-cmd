# coding: utf-8
import tempfile
import pkg_resources
from nose.tools import eq_, ok_
from distutils.version import Version
from mock import patch
from StringIO import StringIO

import acmd


def test_get_current_version():
    v = acmd.get_current_version()
    eq_(True, isinstance(v, Version))
    eq_(acmd.__version__, str(v))

@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_setup_rcfile(stderr, stdout):
    _, path = tempfile.mkstemp(suffix='.acmd-test.rc')
    acmd.setup_rcfile(path)
    template = pkg_resources.resource_string('acmd', "data/acmd.rc.template")
    with open(path, 'rb') as f:
        content = f.read()
        ok_(len(content) > 0)
        eq_(template, content)

@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_deploy_bash_completion(stderr, stdout):
    path = tempfile.mkdtemp(suffix='.acmd.bash_completion.d')
    paths = [path]
    ret = acmd.deploy_bash_completion(paths=paths)
    eq_(path, ret)

@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_no_deploy_dirs(stderr, stdout):
    path = '/THIS/IS/A/NON/EXISTING/PATH'
    ret = acmd.deploy_bash_completion(paths=[path])
    eq_(None, ret)

