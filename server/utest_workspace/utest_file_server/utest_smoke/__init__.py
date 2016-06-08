#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/8

@author: Jay
"""
from utest_lib.common import *
from interfaces.file_server.http_rpc import up_file, down_file
from utest_lib.setting import TEST_USER_NAME
from utest_lib.service import FileSvrHttpRpcClt


class FileServerTest(unittest.TestCase):
    @unittest_adaptor()
    def test_file_up_down_normal(self):
        wav_file = "test.wav"

        up_fn = wav_file.split('\\')[-1]
        file_data = open(wav_file, 'rb').read()
        print "up_fn,", up_fn
        print len(file_data)
        up_file_len = len(file_data)
        up_resp = up_file(FileSvrHttpRpcClt,TEST_USER_NAME, 3, up_fn, file_data)
        print "up_resp,",up_resp

        down_data = down_file(FileSvrHttpRpcClt, TEST_USER_NAME, up_fn, up_resp['r'])
        down_file_len = len(down_data)
        self.assertTrue(up_file_len == down_file_len)