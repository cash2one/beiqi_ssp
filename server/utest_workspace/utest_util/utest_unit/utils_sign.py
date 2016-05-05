#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/5

@author: Jay
"""
from lib.common import *
from util.crypto.sign import sign
from util.sso_common.build_sso_token import parser_token


class UtilSignTest(unittest.TestCase):
    @unittest_adaptor()
    def test_sign1(self):
        http_method = "GET"
        url = "http://api.beiqicloud.com:8302/sign_in"
        params = {"sn": "P081101551000006"}
        secret = "aea8b32e091a11e681ee408d5c5a48ca"
        _sign = "2a6c591eb0d19114304820dd316c2c95"
        my_sign = sign(http_method, url, params, secret)
        self.assertTrue(my_sign == _sign)

    @unittest_adaptor()
    def test_sign2(self):
        #base_str=GEThttp%3A%2F%2Fapi.beiqicloud.com%3A8300%2Fres%2Ffile_tkfn%3D1462436658191.amrm%3D0username%3D13124070068%40jiashu.comb97326b0091a11e697ea408d5c5a48ca, client: 27.154.202.222, server: localhost, request: "GET /res/file_tk?username=13124070068%40jiashu.com&fn=1462436658191.amr&m=0&_tk=bfa336d93571056d229c75c9ad292f9a8f245108c112a7e1b2b13d06548a555c0430db788703158ffaa3270a83504a43ff7270ffbd943f6bb63be60e053cd20cb8d862ffc07ecc57f12123d73969&_sign=f7112cc8c50c9eecd156a715e3bd0e94 HTTP/1.1", host: "api.beiqicloud.com:8300"
        #base_str="GEThttp%3A%2F%2Fapi.beiqicloud.com%3A8300%2Fres%2Ffile_tkfn%3D1462436658191.amrm%3D0username%3D13124070068%40jiashu.comb97326b0091a11e697ea408d5c5a48ca"
        http_method = "GET"
        url = "http://api.beiqicloud.com:8300/res/file_tk"
        params = {"username": "13124070068%40jiashu.com", "fn":"1462436658191.amr", "m":0}
        _tk="bfa336d93571056d229c75c9ad292f9a8f245108c112a7e1b2b13d06548a555c0430db788703158ffaa3270a83504a43ff7270ffbd943f6bb63be60e053cd20cb8d862ffc07ecc57f12123d73969"
        _sign = "f7112cc8c50c9eecd156a715e3bd0e94"

        secret, account, expire = parser_token(_tk)
        my_sign = sign(http_method, url, params, secret)
        self.assertTrue(my_sign == _sign)