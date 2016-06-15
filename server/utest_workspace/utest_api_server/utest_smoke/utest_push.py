#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/15

@author: Jay
"""
from utest_lib.common import *
from interfaces.api_server.http_rpc import bind_push
from utest_lib import gen_test_tk
from util.oem_account_key import APP_SECRET


class APIPushTest(unittest.TestCase):
    def test_push_band_push(self):
        bind_push_res = bind_push(SERVER_IP, gen_test_tk(), APP_SECRET, TEST_USER_NAME, "0.1", "and", "baidu,6529369,878406378381072961,4245279401042655123")
        print bind_push_res