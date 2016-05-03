#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-9-2

@author: Jay
"""
from utils.meta.instance_pool import InstancePool

class Picker(object):

    @classmethod
    def pick_key(cls, k):
        return k

    @classmethod
    def pick_value(cls, v):
        return v

    @classmethod
    def unpick_value(cls, v):
        return v


class CachePicker(Picker):
    __metaclass__ = InstancePool