#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-27

@author: Jay
"""
from lib.common import *
from utils.meta.instance_pool import InstancePool
from utils.meta.singleton import Singleton


class ClassAForIP(object):
    __metaclass__ = InstancePool

    def __init__(self, *args, **kwargs):
        pass

SingletonInstancePool = type("singleton_instancepool", (InstancePool, Singleton), {})
class ClassAForSIP(object):
    __metaclass__ = SingletonInstancePool

    def __init__(self, *args, **kwargs):
        pass

class InstancePoolTest(unittest.TestCase):

    @unittest_adaptor()
    def test_instance_pool(self):
        self.assertTrue(ClassAForIP.instance("a", "b", "c", "d") == ClassAForIP.instance("a", "b", "c", "d"))
        self.assertFalse(ClassAForIP.instance("a", "b", "c", "d") == ClassAForIP.instance("a", "b", "c"))
        self.assertTrue(ClassAForIP.instance("a", {"b", "c"}) == ClassAForIP.instance("a", {"b", "c"}))
        self.assertFalse(ClassAForIP.instance("a", {"b": 1, "c": 2}) == ClassAForIP.instance("a", {"b": 1, "c": 3}))

    @unittest_adaptor()
    def test_instance_pool_singleton(self):
        self.assertTrue(ClassAForSIP.instance("a", {"b": 1, "c": 2}) == ClassAForSIP.instance("a", {"b": 1, "c": 2}))
        self.assertFalse(ClassAForSIP() == ClassAForSIP.instance("a", {"b": 1, "c": 3}))
