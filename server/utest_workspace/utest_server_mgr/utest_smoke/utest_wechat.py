#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-8-20

@author: Jay
"""
from lib.common import *
import unittest
from interfaces.service_mgr.tcp_rpc import get_wc_clt_access_token, get_wc_openid


class ServiceMgrWechatSettingTest(unittest.TestCase):

    # 初始化工作
    def setUp(self):
        pass

    # 退出清理工作
    def tearDown(self):
        pass

    @unittest_adaptor()
    def test_wc_clt_access_token(self):
        wc_clt_access_token = get_wc_clt_access_token(ParamCacher().sm_rpc)
        # 内网不一定可以获取到token
        #self.assertTrue(wc_clt_access_token)

    @unittest_adaptor()
    def test_wc_openid_noexist(self):
        code = "000000000"
        wc_openid = get_wc_openid(ParamCacher().sm_rpc,code)
        self.assertTrue(wc_openid is None)



