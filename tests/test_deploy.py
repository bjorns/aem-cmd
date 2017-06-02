# coding: utf-8
import tempfile
from distutils.version import Version

import pkg_resources
from mock import patch
from nose.tools import eq_, ok_

import acmd

from test_utils.compat import StringIO


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
    eq_('', stdout.getvalue())
    ok_("warning:" in stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_deploy_bash_completion(stderr, stdout):
    path = tempfile.mkdtemp(suffix='.acmd.bash_completion.d')
    paths = [path]
    ret = acmd.deploy_bash_completion(paths=paths)
    eq_(path, ret)
    eq_('', stdout.getvalue())
    eq_('', stderr.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_no_deploy_dirs(stderr, stdout):
    path = '/THIS/IS/A/NON/EXISTING/PATH'
    ret = acmd.deploy_bash_completion(paths=[path])
    eq_(None, ret)
    eq_('', stdout.getvalue())
    eq_('Could not find bash completion install dir.', stderr.getvalue())
