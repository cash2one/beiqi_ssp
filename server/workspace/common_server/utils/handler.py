#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016-4-7

@author: Jay
"""
from utils import logger
from utils.meta.instance_pool import InstancePool

class HandleHolder(object):
    __metaclass__ = InstancePool

    def __init__(self, instance_name):
        self.instance_name = instance_name
        self.key2fun = {}

    def reg_message(self, msg_type, hander_fun):
        self.key2fun[msg_type] = hander_fun

    def handle(self, key, *args, **kwargs):
        if key not in self.key2fun:
            error_msg = "HandleHolder::key:%s not register, key2fun:%s" % (key, self.key2fun)
            logger.error(error_msg)
            return True

        self.key2fun[key](*args, **kwargs)
        return True
