#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/17

@author: Jay
"""
from utest_lib.common import *
from util.oem_account_key import APP_SECRET
from interfaces.api_server.http_rpc import add_code, check_code
from utest_lib import gen_test_tk


class APIETicketTest(unittest.TestCase):
    def test_eticket_check_exist(self):
        code = random.randint(1, 1000000)

        add_res = add_code(SERVER_IP,gen_test_tk(), APP_SECRET, code)
        self.assertTrue(add_res['status'] == 0)

        check_res = check_code(SERVER_IP,gen_test_tk(), APP_SECRET, code)
        self.assertTrue(check_res['status'] == 0)

    def test_eticket_check_not_exist(self):
        code = random.randint(1, 1000000)

        check_res = check_code(SERVER_IP,gen_test_tk(), APP_SECRET, code)
        self.assertTrue(check_res['status'] == 1)

    def test_eticket_check_checked(self):
        code = random.randint(1, 1000000)

        add_res = add_code(SERVER_IP,gen_test_tk(), APP_SECRET, code)
        self.assertTrue(add_res['status'] == 0)

        check_res = check_code(SERVER_IP,gen_test_tk(), APP_SECRET, code)
        self.assertTrue(check_res['status'] == 0)

        check_res = check_code(SERVER_IP,gen_test_tk(), APP_SECRET, code)
        self.assertTrue(check_res['status'] == 3)
