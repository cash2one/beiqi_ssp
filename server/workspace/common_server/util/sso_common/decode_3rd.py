#coding:utf-8


from util.crypto_rc4 import decrypt as rc4_decrypt
from Crypto.Hash import SHA, HMAC
from urlparse import parse_qsl


def check_cipher(cipher, api_secret, sign):
    """
    检查密文和签名
    :param cipher:
    :param api_secret:
    :param sign:
    :return:
    """
    plain = rc4_decrypt(cipher, api_secret)
    if HMAC.new(api_secret, plain, SHA).hexdigest() != sign:
        #签名不一致
        return None

    try:
        return dict(iter(parse_qsl(plain)))
    except ValueError:
        return None
