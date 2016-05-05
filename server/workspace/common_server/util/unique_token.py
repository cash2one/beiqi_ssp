#coding:utf-8


from crypto_rc4 import encrypt, decrypt
from binascii import a2b_hex, b2a_hex
from torn_resp import json


key = '3ff9bbe0d96b4ce2a80776e398d82fd5'


def gen_token(d):
    """
    生成token，统一为dict类型，字段由外部确定
    token由aes加密生成，验证时解密成功并且字段逻辑成功则token校验完成

    :arg d: token fields
    """
    assert d and isinstance(d, dict)
    return encrypt(json.dumps(d), key, b2a_hex)


def val_token(cipher, cb):
    """
    校验token，通过回调函数完成

    :arg cipher: 密文token
    :arg cb: callback
    """
    assert cipher and isinstance(cipher, str)
    plain = decrypt(cipher, key, a2b_hex)
    try:
        plain = json.loads(plain)
    except ValueError:
        return False

    assert cb and callable(cb)
    return cb(plain)
