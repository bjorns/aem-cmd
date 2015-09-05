# coding: utf-8
from nose.tools import eq_, ok_
from distutils.version import Version
import tempfile
import pkg_resources

import acmd


def test_get_current_version():
    v = acmd.get_current_version()
    eq_(True, isinstance(v, Version))
    eq_(acmd.__version__, str(v))

def test_setup_rcfile():
    _, path = tempfile.mkstemp(suffix='.acmd-test.rc')
    acmd.setup_rcfile(path)
    template = pkg_resources.resource_string('acmd', "data/acmd.rc.template")
    with open(path, 'rb') as f:
        content = f.read()
        ok_(len(content) > 0)
        eq_(template, content)

def test_deploy_bash_completion():
    path = tempfile.mkdtemp(suffix='.acmd.bash_completion.d')
    paths = [path]
    ret = acmd.deploy_bash_completion(paths=paths)
    eq_(path, ret)


def test_no_deploy_dirs():
    path = '/THIS/IS/A/NON/EXISTING/PATH'
    ret = acmd.deploy_bash_completion(paths=[path])
    eq_(None, ret)
