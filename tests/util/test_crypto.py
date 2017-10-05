# coding: utf-8
from nose.tools import eq_

from acmd.util.crypto import parse_prop, encode_prop
from acmd.util.crypto import encrypt_str, decrypt_str

def test_prop_save():
    iv = b'This is an iv'
    password = "Password"

    prop = encode_prop(password, iv)
    eq_('{UGFzc3dvcmQKVkdocGN5QnBjeUJoYmlCcGRnPT0=}', prop)

    new_pass, new_iv = parse_prop(prop)

    eq_(password, new_pass)
    eq_(iv, new_iv)


def test_encrypt_decrypt_str():
    iv = b'This is an IV456'
    msg = "Hello Wörld"
    key = b'Some kind of key'

    data = encrypt_str(iv, key, msg)

    eq_("SapMLwk/NqcHuy4y", data)
    new_msg = decrypt_str(iv, key, data)
    eq_(msg, new_msg)
