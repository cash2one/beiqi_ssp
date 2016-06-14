#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-24

@author: Jay
"""
import ujson
from hashlib import md5
from utils.meta.singleton import Singleton


def sign(data):
    """
    RSA签名
    :param data: 需要签名的字符串
    :return:签名后的字符串
    """
    md5_inst = md5()
    md5_inst.update(data)
    return md5_inst.hexdigest()


def checksign(signed_data, data):
    """
    RSA验签
    :param signed_data: 签名后的字符串
    :param data: 签名前的字符串
    :return:如果验签通过，则返回True;如果验签不通过，则返回False
    """
    return signed_data == sign(data)



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
