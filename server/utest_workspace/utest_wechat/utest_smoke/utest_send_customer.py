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
from utest_lib.service import FileSvrHttpRpcClt, FILE_SERVER_PORT
from utest_lib.setting import ACC_RDS_URI, TEST_USER_NAME, SERVER_IP
from interfaces.wechat_server import wechat_customer_service
from util.redis.redis_client import Redis
from interfaces.wechat_server import wechat_file_up

# 在 urllib2 上注册 http 流处理句柄
register_openers()


class WechatFile2WechatTest(unittest.TestCase):
    def test_send_customer_voice(self):
        access_token = gen_wechat_access_token(Redis(ACC_RDS_URI))
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

        payload = {
        "touser": "oGR4dwERXuGRoHiQnSQyavbM6214",
        "msgtype": "voice",
        "voice": {
            "media_id": wechat_up_res['media_id'],
            }
        }

        # 客服消息有时间限制，微信用户如果24小时之内未与微信公众号互动过，则公众号无法向该微信用户发送客服消息。
        print wechat_customer_service(access_token, payload)

    def test_send_customer_image(self):
        access_token = gen_wechat_access_token(Redis(ACC_RDS_URI))
        self.assertTrue(access_token)

        file_path = "test.jpg"
        up_file_data = open(file_path, 'rb').read()
        fn = str(file_path.split('\\')[-1])
        up_resp = up_file(FileSvrHttpRpcClt,TEST_USER_NAME, 3, fn, up_file_data)

        down_url = 'http://{ip}:{port}/down?tk={tk}&r={ref}'.format(
            ip=SERVER_IP,
            port=FILE_SERVER_PORT,
            tk=urllib.quote(gen_file_tk(TEST_USER_NAME, fn, 0, 0)), ref=urllib.quote(up_resp['r']))

        wechat_up_res = wechat_file_up(access_token, down_url, fn, "image")
        self.assertTrue('media_id' in wechat_up_res)

        payload = {
        "touser": "oGR4dwERXuGRoHiQnSQyavbM6214",
        "msgtype": "image",
        "image": {
            "media_id": wechat_up_res['media_id'],
            }
        }

        # 客服消息有时间限制，微信用户如果24小时之内未与微信公众号互动过，则公众号无法向该微信用户发送客服消息。
        print wechat_customer_service(access_token, payload)









