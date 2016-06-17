#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/12

@author: Jay
"""
from utest_lib.common import *
from interfaces.api_server.http_rpc import add_device, list_devs, check_dev_args
from utest_lib import gen_test_tk
from util.oem_account_key import APP_SECRET
from utest_lib import GDevIC, GDevGid


class APIDevTest(unittest.TestCase):
    def test_add_dev(self):
        add_device(SERVER_IP, gen_test_tk(), APP_SECRET,code=GDevIC)

        list_device_res = list_devs(SERVER_IP, gen_test_tk(), APP_SECRET)
        self.assertTrue(isinstance(list_device_res, list))

        check_dev_args_res = check_dev_args(SERVER_IP, gen_test_tk(), APP_SECRET, TEST_SN)
        self.assertTrue(check_dev_args_res['status'] == 0)