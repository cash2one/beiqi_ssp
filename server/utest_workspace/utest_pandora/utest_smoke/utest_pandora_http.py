#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-21

@author: Jay
"""
from utest_lib.common import *
from utest_lib.service import *
from interfaces.pandora.http_rpc import doc, root, services, locate, get_public_key, service_doc

SERVICE_FOR_PANDORA = [
    ST_PANDORA
]

TP_SERVICE_FOR_PANDORA = [
    RT_MQTT,
] = [
    "tp_mysql"
]

class PandoraTest(unittest.TestCase):

    # 初始化工作
    def setUp(self):
        pass

    # 退出清理工作
    def tearDown(self):
        pass

    @unittest_adaptor()
    def test_pandora_http_ping(self):
        self.assertEqual(PandoraHttpClt.ping(), "ping response!")

    @unittest_adaptor()
    def test_pandora_main_interface(self):
        self.assertTrue(doc(PandoraHttpClt))
        self.assertTrue(root(PandoraHttpClt))
        self.assertTrue(get_public_key(PandoraHttpClt))

    @unittest_adaptor()
    def test_pandora_services(self):
        self.assertTrue(services(PandoraHttpClt))
        for service in SERVICE_FOR_PANDORA:
            self.assertTrue(services(PandoraHttpClt, service))

    @unittest_adaptor()
    def test_pandora_locate(self):
        self.assertTrue(locate(PandoraHttpClt, ST_PANDORA))
        for service in SERVICE_FOR_PANDORA:
            self.assertTrue(locate(PandoraHttpClt, service))

    @unittest_adaptor()
    def test_pandora_tp_services(self):
        for service in TP_SERVICE_FOR_PANDORA:
            self.assertTrue(services(PandoraHttpClt, service))

    @unittest_adaptor()
    def test_pandora_tp_locate(self):
        for service in TP_SERVICE_FOR_PANDORA:
            self.assertTrue(locate(PandoraHttpClt, service))

    @unittest_adaptor()
    def test_pandora_service_doc(self):
        for service in SERVICE_FOR_PANDORA:
            self.assertTrue(service_doc(PandoraHttpClt, service))

