#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/5

@author: Jay
"""
from utest_lib.common import *
from utils.crypto.beiqi_sign import sign, gen_url_sign, append_url_sign, append_url_tk, append_url_sign_tk
from util.sso_common.build_sso_token import parser_token


class UtilSignTest(unittest.TestCase):
    @unittest_adaptor()
    def test_sign1(self):
        http_method = "GET"
        url = "http://api.beiqicloud.com:8300/get_user_info"
        params = {"user": "wx%23oGR4dwFIZ8ctCGB52hWNsFVs_rdE"}
        app_secret = "b97326b0091a11e697ea408d5c5a48ca"
        _sign = "8ffda992b2f8c0bf1cb709644aeb5008"
        my_sign = sign(http_method, url, params, app_secret)[-1]
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

        expire, api_secret, account, api_key_head = parser_token(_tk)
        print expire, api_secret, account, api_key_head
        my_sign = sign(http_method, url, params, api_secret)[-1]
        self.assertTrue(str(my_sign) == str(_sign))

    @unittest_adaptor()
    def test_url_sign(self):
        url = "http://api.beiqicloud.com:8300/get_user_info?user=wx%23oGR4dwFIZ8ctCGB52hWNsFVs_rdE"
        app_secret = "b97326b0091a11e697ea408d5c5a48ca"
        _sign = "8ffda992b2f8c0bf1cb709644aeb5008"

        my_sign = gen_url_sign(url, app_secret)[-1]
        self.assertTrue(my_sign == _sign)

    @unittest_adaptor()
    def test_append_url_sign(self):
        url = "http://api.beiqicloud.com:8300/get_user_info?user=wx%23oGR4dwFIZ8ctCGB52hWNsFVs_rdE"
        app_secret = "xxxxxxxxxxxxxx"

        my_sign = gen_url_sign(url, app_secret)[-1]
        should_sign_url = url + "&_sign=%s" % (my_sign)
        sign_url = append_url_sign(url, app_secret)
        self.assertTrue(should_sign_url == sign_url)

    @unittest_adaptor()
    def test_append_url_sign1(self):
        url = "http://api.beiqicloud.com:8302"
        api_secret = "xxxxxxxxxxxxxx"

        my_sign = gen_url_sign(url, api_secret)[-1]
        should_sign_url = url + "?_sign=%s" % (my_sign)
        sign_url = append_url_sign(url, api_secret)
        print sign_url
        print should_sign_url
        self.assertTrue(should_sign_url == sign_url)

    @unittest_adaptor()
    def test_append_url_sign2(self):
        url = "http://124.152.165.189:8302?a=b&c=d"
        api_secret = "adcvdgdvddfdf"

        my_sign = gen_url_sign(url, api_secret)[-1]
        should_sign_url = url + "&_sign=%s" % (my_sign)
        sign_url = append_url_sign(url, api_secret)
        print sign_url
        print should_sign_url
        self.assertTrue(should_sign_url == sign_url)

    @unittest_adaptor()
    def test_append_url_tk_sign(self):
        api_secret = "adcvdgdvddfdf"

        url = "http://124.152.165.189:8302"
        my_sign = gen_url_sign(url, api_secret)[-1]
        tk = "adfadfadfasfsadfasf"

        should_sign_tk_url = url + "?_sign=%s&_tk=%s" % (my_sign, tk)
        sign_tk_url = append_url_sign_tk(url, tk, api_secret)
        self.assertTrue(should_sign_tk_url == sign_tk_url)


        url = "http://124.152.165.189:8302?a=b&c=d"
        my_sign = gen_url_sign(url, api_secret)[-1]
        tk = "adfadfadfasfsadfasf"
        should_sign_tk_url = url + "&_sign=%s&_tk=%s" % (my_sign, tk)
        sign_tk_url = append_url_sign_tk(url, tk, api_secret)
        print should_sign_tk_url
        self.assertTrue(should_sign_tk_url == sign_tk_url)


    @unittest_adaptor()
    def test_append_url_tk(self):
        url = "http://124.152.165.189:8302"
        tk = "adfadfadfasfsadfasf"
        should_tk_url = url + "?_tk=%s" % (tk)
        tk_url = append_url_tk(url, tk)
        self.assertTrue(should_tk_url == tk_url)


        url = "http://124.152.165.189:8302?a=b&c=d"
        tk = "adfadfadfasfsadfasf"
        should_tk_url = url + "&_tk=%s" % (tk)
        tk_url = append_url_tk(url, tk)
        self.assertTrue(should_tk_url == tk_url)
