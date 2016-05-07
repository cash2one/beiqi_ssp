#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/6

@author: Jay
"""
from lib.common import *
from utils.network.http import HttpRpcClient
from util.oem_account_key import APP_KEY, beiqi_keys
from util.sso_common.build_sso_token import parser_token

class SSOServerGenTKTest(unittest.TestCase):
    @unittest_adaptor()
    def test_gen_tk_normal(self):
        user_name = '15750701209@jiashu.com'
        pwd = '123456'
        url = "http://localhost:8104/gen_tk?username={0}&pwd={1}&api_key={2}".format(user_name, pwd, APP_KEY)
        token = HttpRpcClient().fetch_async(url=url)
        expire, secret, account, api_key = parser_token(token)
        self.assertTrue(account == user_name)
        self.assertTrue(secret == beiqi_keys[APP_KEY]['s'])
