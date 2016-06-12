#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/12

@author: Jay
"""
import unittest
from interfaces.dev_server.http_rpc import sign_in
from utest_lib import gen_test_tk
from utest_lib.setting import TEST_SN, SERVER_IP, DEV_SERVER_PORT
from util.sso_common.build_sso_token import encrypt_username
from util.oem_account_key import DEV_KEY, DEV_RC4, DEV_SECRET


class DEVSigninTest(unittest.TestCase):
    def test_dev_signin(self):
        dev_tk = gen_test_tk(encrypt_username(TEST_SN, DEV_RC4), app_key=DEV_KEY, dev_rc4=DEV_RC4)
        sign_in_res = sign_in(SERVER_IP, dev_tk, DEV_SECRET, TEST_SN, DEV_SERVER_PORT)
        self.assertTrue(sign_in_res['status'] == 0)
        self.assertTrue(sign_in_res['gid'])