#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-22

@author: Jay
"""
from utils import  error_code


def assertHrpcSuccess(utest_obj, expr, msg=None):
    utest_obj.assertTrue(expr['result'] == error_code.ERROR_SUCCESS)


def assertHrpcFail(utest_obj, expr, msg=None):
    utest_obj.assertFalse(expr['result'] == error_code.ERROR_SUCCESS)