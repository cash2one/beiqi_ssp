#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-6-23

@author: Jay
"""

def set_cookie(request_hdl, k, v, expires_time):
    request_hdl.set_secure_cookie(k, v, expires=expires_time)


def check_cookie(request_hdl, k, v_check, clear=True):
    v_in_cookie = request_hdl.get_secure_cookie(k)
    if clear:
        request_hdl.clear_cookie(k)
    # 不区分大小写
    return v_in_cookie.lower() == v_check.lower() if v_in_cookie else False
