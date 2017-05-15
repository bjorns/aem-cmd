# coding: utf-8
from nose.tools import eq_
from . import mock_service


def test_mock_assets_service():
    s = mock_service.MockAssetsService()
    eq_(1, len(s.repo))
    s.add_folder('/', 'my_folder')
    eq_(2, len(s.repo))
    eq_(s.repo['/'], s.repo['/my_folder']['parent'])
    s.add_asset('/my_folder', 'bernard.jpg')
    eq_(1, len(s.repo['/my_folder']['assets']))
    eq_(s.repo['/my_folder/bernard.jpg'], s.repo['/my_folder']['assets'][0])
