# coding: utf-8
from nose.tools import eq_

from acmd.filter import matches, FileFilter


def test_matches():
    filter_obj = {
        'filetypes': ['png']
    }
    eq_(True, matches(filter_obj, 'foobar.png'))
    eq_(True, matches(filter_obj, 'png'))
    eq_(False, matches(filter_obj, 'foobar.jpg'))

    filter_obj = {
        'paths': ['filtered_dir/']
    }
    eq_(False, matches(filter_obj, 'ok_dir/foobar.png'))
    eq_(True, matches(filter_obj, 'filtered_dir/foobar.jpg'))


def test_file_filter():
    file_filter = FileFilter('tests/test_data/test_filter_both.json')
    eq_(True, file_filter.accept('foobar.png'))
    eq_(True, file_filter.accept('png'))
    eq_(True, file_filter.accept('foobar.jpg'))
    eq_(True, file_filter.accept('/Users/bjorn/Images/good_ones/test.png'))
    eq_(False, file_filter.accept('/Users/bjorn/Images/good_ones/exception/test.png'))
    eq_(False, file_filter.accept('/Users/bjorn/Images/.DS_Store'))
    eq_(False, file_filter.accept('essay.docx'))

