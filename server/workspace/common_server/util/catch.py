#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/20

@author: Jay
"""

import traceback
import sys
from utils import logger


def except_adaptor(is_raise=True, default_result=None):
    def except_fun_adaptor(fun):
        def except_param_adptor(*args, **kwargs):
            try:
                return fun(*args, **kwargs)
            except:
                exec_info = sys.exc_info()
                track_back_data = "%s Error!!!!!!!!!!!!!\n" % fun.__name__
                track_back_data += str(exec_info[0]) + ":" + str(exec_info[1]) + '\n'
                track_back_data += traceback.format_exc()
                logger.error(track_back_data)
                if is_raise:
                    raise
            if default_result:
                return default_result
        return except_param_adptor
    return except_fun_adaptor
