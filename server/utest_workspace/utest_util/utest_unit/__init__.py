#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/5

@author: Jay
"""
from lib.common import *
from utils.comm_func import make_unique_id
from util.sso_common.build_sso_token import gen_token, parser_token


class SignTest(unittest.TestCase):

    @unittest_adaptor()
    def test_token(self):
        api_secret = make_unique_id()
        username = random_str()
        expire_days = random.randint(0,100)

        token = gen_token(api_secret, username, expire_days)
        secret, account, expire = parser_token(token)

        self.assertTrue(api_secret == secret)
        self.assertTrue(username == account)
        self.assertTrue(int(time.time() + 86400 * expire_days) == expire)

