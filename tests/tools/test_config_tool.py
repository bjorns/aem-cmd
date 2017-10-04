# coding: utf-8
from nose.tools import eq_

from acmd.tools.config_tool import encrypt_str, decrypt_str

IV = b'This is an IV456'

def test_encrypt_decrypt_str():
    msg = "Hello World"
    key = "Some kind of key"
    data = encrypt_str(IV, key, msg)
    eq_(b'SapMLwk/NgtXqPY=', data)
    new_msg = decrypt_str(IV, key, data)
    eq_(msg, new_msg)
