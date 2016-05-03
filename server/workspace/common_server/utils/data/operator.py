#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-9-1

@author: Jay
"""
from utils.meta.instance_pool import InstancePool

class Operator(object):
    @classmethod
    def set(cls, key, value):
        pass

    @classmethod
    def get(cls, key):
        return {}

    @classmethod
    def get_ls(cls, key_ls):
        return [cls.get(key) for key in key_ls]

    @classmethod
    def del_ls(cls, key_ls):
        pass

    @classmethod
    def check(cls, data):
        pass

class StorageOperator(Operator):
    __metaclass__ = InstancePool

