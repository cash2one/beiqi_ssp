#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-7

@author: Jay
"""
from interfaces.sso_server.http_rpc import gen_tk
from utest_lib.setting import TEST_USER_NAME, TEST_PASSWD
from utest_lib.service import SSOHttpRpcClt
from util.oem_account_key import APP_KEY, DEV_RC4


def gen_test_tk(user_name=TEST_USER_NAME, app_key=APP_KEY, dev_rc4=DEV_RC4):
    return gen_tk(SSOHttpRpcClt, user_name , user_name, app_key, dev_rc4)