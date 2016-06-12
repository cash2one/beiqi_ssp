#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/12

@author: Jay
"""
import random
import unittest
from interfaces.api_server.http_rpc import add_device
from utest_lib import gen_test_tk
from utest_lib.setting import SERVER_IP
from util.oem_account_key import APP_SECRET
from utest_lib import GDevIC


class APIAddDevTest(unittest.TestCase):
    def test_add_dev(self):
        add_device_res = add_device(SERVER_IP, gen_test_tk(), APP_SECRET,code=GDevIC)
        print add_device_res