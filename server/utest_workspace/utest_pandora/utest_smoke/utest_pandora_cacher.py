#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-24

@author: Jay
"""
from lib.common import *
from lib.service import *
from utils.service_control.cacher import PandoraCacher


class PandoraCacherTest(unittest.TestCase):
    pc = PandoraCacher(PandoraHttpClt.host, PandoraHttpClt.port)

    @unittest_adaptor()
    def test_pandora_http_ping(self):
        self.assertEqual(PandoraHttpClt.ping(), "ping response!")

    @unittest_adaptor()
    def test_pandora_cacher_normal(self):
        self.assertTrue(self.pc.locate(ST_PANDORA))

    @unittest_adaptor()
    def test_pandora_cacher_abnormal(self):
        self.assertTrue(self.pc.locate("sssssssss") is None)
        self.assertTrue(self.pc.locate("aaaaaaaa") is None)
        self.assertTrue(self.pc.locate("cccccccc") is None)

