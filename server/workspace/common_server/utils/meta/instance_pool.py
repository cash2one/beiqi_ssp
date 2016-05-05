#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-27

@author: Jay
"""
import ujson

class InstancePool(type):
    instances = {}

    def __init__(cls, name, bases, dict_value):
        super(InstancePool, cls).__init__(name, bases, dict_value)

    def instance(cls, *args, **kwargs):
        key = ujson.dumps([str(arg) for arg in args ]) if args else ""
        key += ujson.dumps(kwargs) if kwargs else ""
        ins = cls.instances.get(key, None)
        if not ins:
            ins = super(InstancePool, cls).__call__(*args, **kwargs)
            cls.instances[key] = ins
        return ins
