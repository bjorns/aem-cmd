# coding: utf-8
from nose.tools import eq_

from acmd.tools.asset_import import UploadRegistry


def test_lock_file_path():
    reg = UploadRegistry(None, None, force_root='/tmp/test_root')
    eq_('/tmp/test_root/foobar/test', reg._lock_file('foobar/test'))


def test_windows_lock_file_path():
    reg = UploadRegistry(None, None, force_root='C:\\tmp\\test_root')
    eq_('C:\\tmp\\test_root/foobar\\test', reg._lock_file('foobar\\test', os_name='windows'))
