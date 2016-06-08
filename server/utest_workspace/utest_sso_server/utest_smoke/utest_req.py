#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/6

@author: Jay
"""
from utest_lib.common import *
from util.oem_account_key import APP_KEY, beiqi_keys
from util.sso_common.build_sso_token import parser_token
from interfaces.sso_server.http_rpc import req_reg_val_code, check_reg_val_code
from utest_lib.setting import TEST_USER_NAME
from utest_lib.service import SSOHttpRpcClt
from utest_lib import gen_test_tk


class SSOServerGenTKTest(unittest.TestCase):
    @unittest_adaptor()
    def test_gen_tk_normal(self):
        token = gen_test_tk()
        expire, secret, account, api_key = parser_token(token)
        self.assertTrue(account == TEST_USER_NAME)
        self.assertTrue(secret == beiqi_keys[APP_KEY]['s'])

    @unittest_adaptor()
    def test_req_reg_val_code(self):
        resp = req_reg_val_code(SSOHttpRpcClt, account=TEST_USER_NAME)
        print resp
        self.assertTrue(resp['status'] in [0, 4])

    @unittest_adaptor()
    def test_check_reg_val_code(self):
        resp = check_reg_val_code(SSOHttpRpcClt, account=TEST_USER_NAME, pwd=random_str(6), val=random_str(6))
        self.assertTrue(resp['status'] == 3)

