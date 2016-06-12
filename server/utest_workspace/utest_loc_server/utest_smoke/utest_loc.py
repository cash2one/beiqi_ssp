#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/12

@author: Jay
"""
import unittest
from interfaces.loc_server.http_rpc import location
from utest_lib.service import LocSvrHttpRpcClt


class APILocationTest(unittest.TestCase):
    def test_get_location(self):
        param = {
            "accesstype": 1,
            "imei": "355440073090762",
            "smac": "C0:CC:F8:E7:E2:C5",
            "macs": "00:0C:43:30:92:00,-45,NS3000G|D4:EE:07:39:BA:12,-65,ZuiPin-AP04|C0:A0:BB:F7:7C:58,-64,huiming",
        }

        #  这里需要后台授权开启测试ip，所以返回值为：INVALID_USER_IP
        loc_result = location(LocSvrHttpRpcClt, **param)
        self.assertTrue(loc_result['status' == 0])