#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-20

@author: Jay
"""
import random
from utils import logger

sample_str = "zyxwvutsrqponmlkjihgfedcba"


def random_str(str_len=6):
    return ''.join(random.sample(sample_str, str_len))


def unittest_adaptor():
    def unittest_fun_adaptor(fun):
        def unittest_param_adaptor(self, *args, **kwargs):
            #print "start unittest:%s" % fun.__name__
            logger.warn("start unittest:%s" % fun.__name__)
            return fun(self, *args, **kwargs)
        return unittest_param_adaptor
    return unittest_fun_adaptor
