#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/16

@author: Jay
"""
from utest_lib.common import *
from interfaces.api_server.http_rpc import get_user_info
from utest_lib import gen_test_tk
from util.oem_account_key import APP_SECRET


class APIAccountTest(unittest.TestCase):
    def test_get_user_info(self):
        user_info = get_user_info(SERVER_IP, gen_test_tk() , APP_SECRET)
        print user_info
        self.assertTrue(isinstance(user_info, dict))