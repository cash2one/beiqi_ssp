#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-8-17

@author: Jay
"""
from lib.common import *
from utils.wechat.signature import SignatureChecker
from utils.setting.wechat import TOKEN

class WechatTest(unittest.TestCase):
    @unittest_adaptor()
    def test_recv_signature(self):
        kwargs ={'nonce': '343523234',
                 'timestamp': '1439794060',
                 'encrypt_type': 'aes',
                 'msg_signature': 'd60185aee89d837f54fb05e4d1b9fe5892394934',
                 'signature': 'd3727b8b8c83a52a86a1b83f2aceae554a30ef4c'}
        self.assertTrue(SignatureChecker().check(TOKEN,
                                                 kwargs['timestamp'],
                                                 kwargs['nonce'],
                                                 kwargs['signature']))


