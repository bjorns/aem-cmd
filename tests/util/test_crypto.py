# coding: utf-8
from nose.tools import eq_

from acmd.util.crypto import encrypt_str, decrypt
from acmd.util.crypto import parse_prop, encode_prop, IV_BLOCK_SIZE


def test_prop_save():
    iv = b'1234123412341234'
    salt = b'0123456789abcdef'
    eq_(IV_BLOCK_SIZE, len(iv))
    ciphertext = b"ciphertext"

    prop = encode_prop(iv, salt, ciphertext)
    eq_('{MTIzNDEyMzQxMjM0MTIzNDAxMjM0NTY3ODlhYmNkZWZjaXBoZXJ0ZXh0}', prop)

    new_iv, new_salt, new_pass,  = parse_prop(prop)

    eq_(ciphertext, new_pass)
    eq_(iv, new_iv)
    eq_(salt, new_salt)


def test_encrypt_decrypt_str():
    iv = b'This is an IV456'
    msg = "Hello Wörld"
    key = b'Some kind of key'

    ciphertext = encrypt_str(iv, key, msg)

    eq_(b'I\xaaL/\t?6\xa7\x07\xbb.2', ciphertext)
    new_msg = decrypt(iv, key, ciphertext)
    eq_(msg, new_msg)
