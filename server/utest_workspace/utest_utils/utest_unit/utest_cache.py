#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-8-28

@author: Jay
"""
from lib.common import *
from utils.data.cache import CacheLoader, CacheMgr
from utils.comm_func import random_str

test_data = {random_str(): random_str(), random_str(): random_str()}

class TestLoader(CacheLoader):
    @classmethod
    def load(cls, key):
        return test_data

    @classmethod
    def load_ls(cls, key_ls, **kwargs):
        return [test_data for _ in key_ls]

    @classmethod
    def check(cls, data):
        assert isinstance(data, dict)

test_cache_mgr = CacheMgr.instance(TestLoader)

class CacheTest(unittest.TestCase):

    # 初始化工作
    def setUp(self):
        pass

    # 退出清理工作
    def tearDown(self):
        pass

    @unittest_adaptor()
    def test_cache_set(self):
        test_set_key = random_str(3)
        self.assertTrue(test_cache_mgr.get(test_set_key) == test_data)

        test_set_data = {random_str(): random_str()}
        test_cache_mgr.set(test_set_key, test_set_data)
        self.assertTrue(test_cache_mgr.get(test_set_key) == test_set_data)

        test_set_data = {"test": 1}
        test_cache_mgr.set(test_set_key, test_set_data)
        self.assertTrue(test_cache_mgr.get(test_set_key) == test_set_data)

        test_set_data = {random_str(): random_str()}
        test_cache_mgr.set(test_set_key, test_set_data)
        self.assertTrue(test_cache_mgr.get(test_set_key) == test_set_data)

    @unittest_adaptor()
    def test_cache_get(self):
        test_set_key = random_str(3)
        self.assertTrue(test_cache_mgr.get(test_set_key) == test_data)

    @unittest_adaptor()
    def test_cache_get_ls(self):
        get_len = 10
        keys = [random_str(3) for _ in xrange(get_len)]
        caches = test_cache_mgr.get_ls(keys)
        self.assertTrue(len(caches) == get_len)
        [self.assertTrue(caches[idx] == test_data) for idx, _ in enumerate(keys)]

    @unittest_adaptor()
    def test_cache_has(self):
        test_set_key = random_str(3)
        self.assertTrue(not test_cache_mgr.has(test_set_key))
        test_cache_mgr.get(test_set_key)
        self.assertTrue(test_cache_mgr.has(test_set_key))

    @unittest_adaptor()
    def test_cache_pop(self):
        test_set_key = random_str(3)
        self.assertTrue(test_cache_mgr.get(test_set_key) == test_data)
        test_cache_mgr.pop(test_set_key)
        self.assertTrue(not test_cache_mgr.has(test_set_key))

    @unittest_adaptor()
    def test_cache_pop_ls(self):
        ls_len = 3
        key_ls = [random_str(3) for _ in xrange(ls_len)]
        [test_cache_mgr.get(k) for k in key_ls]
        test_cache_mgr.pop_ls(key_ls)

        for k in key_ls:
            self.assertTrue(not test_cache_mgr.has(k))

    @unittest_adaptor()
    def test_cache_expire(self):
        cache_expire_second = 3
        test_cache_mgr = CacheMgr.instance(TestLoader, cache_expire_second)
        test_set_key = random_str(3)
        self.assertTrue(test_cache_mgr.get(test_set_key) == test_data)
        time.sleep(cache_expire_second * 2)
        self.assertTrue(test_cache_mgr.has(test_set_key) is None)

        self.assertTrue(test_cache_mgr.get(test_set_key) == test_data)

    @unittest_adaptor()
    def test_cache_expire_extend(self):
        cache_expire_second = 3
        test_cache_mgr = CacheMgr.instance(TestLoader, cache_expire_second)
        test_set_key = random_str(3)
        self.assertTrue(test_cache_mgr.get(test_set_key) == test_data)

        reget_times = 3
        for _ in xrange(reget_times):
            time.sleep(cache_expire_second)
            test_cache_mgr.get(test_set_key)

        self.assertTrue(test_cache_mgr.has(test_set_key))