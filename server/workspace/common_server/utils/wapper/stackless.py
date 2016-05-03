#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-30

@author: Jay
"""
import traceback
from functools import wraps
import urllib2
import gevent.pool
from utils.meta.singleton import Singleton
from utils import logger


def gevent_adaptor(use_join_result=True):
    """
    使用gevent异步访问
    """
    def gevent_fun_adaptor(fun):
        def gevent_param_adaptor(*args, **kwargs):
            thread = GreentletGroup().spawn(fun, *args, **kwargs)
            if use_join_result:
                thread.join()
                if isinstance(thread.value,  Exception):
                    raise thread.value
                return thread.value
            return thread
        return gevent_param_adaptor
    return gevent_fun_adaptor

class GreentletGroup(gevent.pool.Pool):
    __metaclass__ = Singleton
    PoolSize = 10000

    def __init__(self, *args):
        super(GreentletGroup, self).__init__(self.PoolSize, *args)
        self._error_handlers = {}

    def _wrap_errors(self, func):
        @wraps(func)
        def wrapped_f(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except urllib2.HTTPError, e:
                return e
            except Exception, e:
                error = traceback.format_exc()
                self.exception_handle(error, *args, **kwargs)
                return e
        return wrapped_f

    @staticmethod
    def exception_handle(error, *args, **kwargs):
        logger.error("args = %s, kwargs = %s \n %s", args, kwargs, error)

    def spawn(self, func, *args, **kwargs):
        parent = super(GreentletGroup, self)
        func_wrap = self._wrap_errors(func)
        return parent.spawn(func_wrap, *args, **kwargs)

    def spawn_later(self, seconds, func, *args, **kwargs):
        parent = super(GreentletGroup, self)
        func_wrap = self._wrap_errors(func)
        return parent.spawn_later(seconds, func_wrap, *args, **kwargs)
