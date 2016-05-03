#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-8-28

@author: Jay
"""
import time
from utils.scheduler import Jobs
from utils.meta.instance_pool import InstancePool


CACHE_EXPIRE_SECOND = (3600 * 8)
CACHE_EXPIRE_CHECK_SECOND = 1

class CacheLoader(object):
    @classmethod
    def load(cls, key, **kwargs):
        return {}

    @classmethod
    def load_ls(cls, key_ls, **kwargs):
        return [cls.load(key) for key in key_ls]

    @classmethod
    def check(cls, data):
        pass


class _Cache(object):
    def __init__(self, loader, key, value=None):
        self.__access_time = time.time()
        self.__data = None
        self.loader = loader
        self.data = key, value

    @property
    def access_time(self):
        return self.__access_time

    def refresh(self):
        self.__access_time = time.time()

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, tp):
        key, value = tp
        data = value if value else self.loader.load(key)
        self.loader.check(data)
        self.__data = data

    def __str__(self):
        return str(self.__data)


class CacheMgr(object):
    __metaclass__ = InstancePool

    def __init__(self, loader_cls, expire_second=CACHE_EXPIRE_SECOND, expire_check_second=CACHE_EXPIRE_CHECK_SECOND):
        self.cache_dic = dict()
        self.loader_cls = loader_cls
        self.expire_second = expire_second
        self.expire_check_second = expire_check_second

        Jobs().add_interval_job(self.expire_check_second, self._cache_expire)
        Jobs().start()

    def set(self, key, value):
        cache = self.cache_dic[key] = _Cache(self.loader_cls, key, value)
        cache.refresh()
        return cache

    def get(self, key):
        cache = self.cache_dic.setdefault(key, _Cache(self.loader_cls, key))
        cache.refresh()
        return cache.data

    def get_ls(self, keys):
        assert isinstance(keys, list)

        miss_cache_ls = [key for key in keys if not self.has(key)]
        data_ls = self.loader_cls.load_ls(miss_cache_ls)
        assert data_ls
        [self.set(key, data_ls[idx]) for idx, key in enumerate(miss_cache_ls)]

        return [self.get(key) for key in keys]

    def has(self, key):
        return self.cache_dic.get(key, None)

    def pop(self, key):
        self.cache_dic.pop(key, None)

    def pop_ls(self, keys):
        assert isinstance(keys, list)
        return [self.pop(key) for key in keys]

    def _cache_expire(self):
        [self.pop(key)
         for key, cache in self.cache_dic.items()
         if cache.access_time + self.expire_second < time.time()]


