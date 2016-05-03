#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-6

@author: Jay
"""
from utils.network.ws import WSRpcApplication

def ws_handler(type):
    def ws_handler_fun_adaptor(handler_fun):
        WSRpcApplication.reg_message(type, handler_fun)
        return handler_fun
    return ws_handler_fun_adaptor
