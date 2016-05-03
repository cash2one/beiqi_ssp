#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-9-1

@author: Jay
"""
from operator import Operator
from utils.meta.instance_pool import InstancePool


class Coordinator(Operator):
    def __init__(self, cache_operator, storage_operator, picker, cache_timeout):
        pass

class CacheCoordinator(Coordinator):
    __metaclass__ = InstancePool

