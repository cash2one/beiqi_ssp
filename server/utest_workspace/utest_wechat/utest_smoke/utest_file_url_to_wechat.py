#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/16

@author: Jay
"""
import sys
import unittest
print sys.path
import urllib
from poster.streaminghttp import register_openers
from util.filetoken import gen_file_tk
from util.wechat import gen_wechat_access_token
from interfaces.file_server.http_rpc import up_file
from utest_lib.service import FileSvrHttpRpcClt, FILE_SERVER_PORT, GCalcRdsInts
from utest_lib.setting import TEST_USER_NAME, SERVER_IP
from interfaces.wechat_server import wechat_file_up, wechat_file_down

# 在 urllib2 上注册 http 流处理句柄
register_openers()


class WechatFile2WechatTest(unittest.TestCase):
    def test_upload_file_to_wechat(self):
        access_token = gen_wechat_access_token(GCalcRdsInts)
        self.assertTrue(access_token)

        mp3_path = "test.mp3"
        up_file_data = open(mp3_path, 'rb').read()
        fn = str(mp3_path.split('\\')[-1])
        up_resp = up_file(FileSvrHttpRpcClt,TEST_USER_NAME, 3, fn, up_file_data)

        down_url = 'http://{ip}:{port}/down?tk={tk}&r={ref}'.format(
            ip=SERVER_IP,
            port=FILE_SERVER_PORT,
            tk=urllib.quote(gen_file_tk(TEST_USER_NAME, fn, 0, 0)), ref=urllib.quote(up_resp['r']))

        wechat_up_res = wechat_file_up(access_token, down_url, fn)
        self.assertTrue('media_id' in wechat_up_res)
        wechat_down_res = wechat_file_down(access_token, wechat_up_res['media_id'])
        self.assertTrue(len(wechat_down_res) > 0)








