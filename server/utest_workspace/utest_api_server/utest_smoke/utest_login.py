#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/16

@author: Jay
"""
from utest_lib.common import *
from interfaces.api_server.http_rpc import list_devs
from utest_lib import gen_test_tk
from util.oem_account_key import APP_SECRET


class APILoginTest(unittest.TestCase):
    def test_login(self):
        tk1 = gen_test_tk()
        list_devs(SERVER_IP, tk1 , APP_SECRET)

        time.sleep(SYNC_WAIT_TIME)

        tk2 = gen_test_tk()
        list_devs(SERVER_IP, tk2 , APP_SECRET)

        # 使用tk1，报错，409
        self.assertRaises(Exception, list_devs, SERVER_IP, tk1 , APP_SECRET)
