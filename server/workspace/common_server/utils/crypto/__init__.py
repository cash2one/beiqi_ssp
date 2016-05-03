#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-24

@author: Jay
"""
import urllib
import base64
from utils.meta.singleton import Singleton
from utils.meta.instance_pool import InstancePool
from utils.crypto import xxtea


SingletonInstancePool = type("singleton_instancepool", (InstancePool, Singleton), {})


class UrlCrypto(object):
    __metaclass__ = SingletonInstancePool

    def __init__(self):
        pass

    def encrypt(self, data):
        data = urllib.quote(data)
        data = data.strip()
        return data

    def decrypt(self, data):
        data = urllib.unquote(data)
        data = data.strip()
        return data

    def __str__(self):
        return self.__class__.__name__

class XXTEACrypto(UrlCrypto):

    def __init__(self, xxtea_key):
        self.x = xxtea.XXTEA(xxtea_key)

    def encrypt(self, data):
        data = self.x.encrypt(data)
        data = base64.b64encode(data, altchars="*-")
        data = super(XXTEACrypto, self).encrypt(data)
        return data

    def decrypt(self, data):
        data = str(data)
        data = super(XXTEACrypto, self).decrypt(data)
        data = base64.b64decode(data, altchars="*-")
        data = self.x.decrypt(data)
        data = data.strip()
        return data