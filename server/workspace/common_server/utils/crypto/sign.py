#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-24

@author: Jay
"""
import os
import base64
import ujson
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5


from utils.meta.singleton import Singleton

private_key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "CA", "server.key")
public_key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "CA", "server_public.key")

public_key = RSA.importKey(open(public_key_path, 'r').read())
private_key = RSA.importKey(open(private_key_path, 'r').read())


def sign(data):
    """
    RSA签名
    :param data: 需要签名的字符串
    :return:签名后的字符串
    """
    sha_obj = SHA.new(data)
    signer = PKCS1_v1_5.new(private_key)
    signed_data = signer.sign(sha_obj)
    signed_data = base64.b64encode(signed_data)
    return signed_data


def checksign(signed_data, data):
    """
    RSA验签
    :param signed_data: 签名后的字符串
    :param data: 签名前的字符串
    :return:如果验签通过，则返回True;如果验签不通过，则返回False
    """
    sha_obj = SHA.new(data)
    signed_data = base64.b64decode(signed_data)
    verifier = PKCS1_v1_5.new(public_key)
    return verifier.verify(sha_obj, signed_data)



class Signer(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.signs = {}

    def _gen_key(self, *args, **kwargs):
        key = ":".join([str(arg) for arg in args])
        key += ujson.dumps(kwargs) if kwargs else ""
        return key

    def gen_sign(self, *args, **kwargs):
        key = self._gen_key(*args, **kwargs)
        if key not in self.signs:
            self.signs[key] = sign(key)
        return self.signs[key]

    def check_sign(self, signed_data, *args, **kwargs):
        key = self._gen_key(*args, **kwargs)
        return checksign(signed_data, key)
