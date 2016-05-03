#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-28

@author: Jay
"""
from utils.handler import HandleHolder

def hold_handle_wapper(handle_holder, key):
    def hold_handle_fun_wapper(handler_fun):
        assert isinstance(handle_holder, HandleHolder)
        handle_holder.reg_message(key, handler_fun)
        return handler_fun
    return hold_handle_fun_wapper
