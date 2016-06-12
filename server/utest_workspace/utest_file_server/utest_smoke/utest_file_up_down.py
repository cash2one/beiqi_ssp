#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/12

@author: Jay
"""
from utest_lib.common import *
from interfaces.file_server.http_rpc import up_file, down_file, delete_file, gen_leveldb_file
from utest_lib.setting import TEST_USER_NAME
from utest_lib.service import FileSvrHttpRpcClt, GCalcRdsInts


class FileServerTest(unittest.TestCase):
    @unittest_adaptor()
    def test_file_up_down_normal(self):
        wav_file = "test.wav"
        if platform.system() != 'Linux':
            wav_file = r"C:\Users\151117a\Desktop\res\%s" % wav_file.decode('utf8')

        up_fn = wav_file.split('\\')[-1]
        file_data = open(wav_file, 'rb').read()
        up_file_len = len(file_data)
        up_resp = up_file(FileSvrHttpRpcClt,TEST_USER_NAME, 3, up_fn, file_data)

        down_data = down_file(FileSvrHttpRpcClt, TEST_USER_NAME, up_fn, up_resp['r'])
        down_file_len = len(down_data)
        self.assertTrue(up_file_len == down_file_len)

    @unittest_adaptor()
    def test_file_up_del_normal(self):
        wav_file = "test.wav"
        if platform.system() != 'Linux':
            wav_file = r"C:\Users\151117a\Desktop\res\%s" % wav_file.decode('utf8')

        up_fn = wav_file.split('\\')[-1]
        file_data = open(wav_file, 'rb').read()
        up_resp = up_file(FileSvrHttpRpcClt,TEST_USER_NAME, 3, up_fn, file_data)

        file = gen_leveldb_file(GCalcRdsInts, TEST_USER_NAME, 3, up_fn)

        delete_result = delete_file(FileSvrHttpRpcClt, TEST_USER_NAME, file)
        self.assertTrue(delete_result['status'] == 0)

        self.assertRaises(Exception, down_file, FileSvrHttpRpcClt, TEST_USER_NAME, up_fn, up_resp['r'])