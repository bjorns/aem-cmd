# coding: utf-8
import base64

from acmd.compat import AES, Random
from acmd.compat import bytestring, stdstring

IV_BLOCK_SIZE = 16


def parse_prop(prop):
    """ Reads property and outputs tuple (encrypted_password, iv) """
    if not (prop.startswith('{') and prop.endswith('}')):
        raise Exception('Unexpected format of prop {}'.format(prop))
    payload = prop[1:-1]
    tmp = base64.b64decode(payload)
    lines = tmp.split(b'\n')
    encrypted_password = stdstring(lines[0])
    iv_str = lines[1]

    iv_bytes = base64.b64decode(iv_str)

    return encrypted_password, iv_bytes


def encode_prop(encrypted_password, iv_bytes):
    assert type(encrypted_password) == str
    assert type(iv_bytes) == bytes

    iv_str = stdstring(base64.b64encode(iv_bytes))

    tmp = "{password}\n{iv}".format(password=encrypted_password, iv=iv_str)
    payload = base64.b64encode(bytestring(tmp))
    return "{" + stdstring(payload) + "}"


def encrypt_str(iv, key, plaintext):
    """ Takes strings in and is expected to give strings out.
        All binary string conversion is internal only.

        iv: 16 character standard string
        key: bytes array
        plaintext: standard string
    """
    assert type(iv) == bytes
    assert type(key) == bytes
    assert type(plaintext) == str

    codec = AES.new(bytestring(key), AES.MODE_CFB, iv)
    bindata = codec.encrypt(bytestring(plaintext))
    return stdstring(base64.b64encode(bindata))


def decrypt_str(iv, key, ciphertext):
    """ Takes strings in and is expected to give strings out.
        All binary string conversion is internal only. """
    assert type(iv) == bytes
    assert type(key) == bytes
    assert type(ciphertext) == str

    bindata = base64.b64decode(bytestring(ciphertext))
    codec = AES.new(bytestring(key), AES.MODE_CFB, bytestring(iv))
    return stdstring(codec.decrypt(bindata))


def generate_iv():
    """ Generate initial vector for encryption
        Returns string of base64
     """
    ret = Random.new().read(IV_BLOCK_SIZE)
    assert type(ret) == bytes
    return ret
