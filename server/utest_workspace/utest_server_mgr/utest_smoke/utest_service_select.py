#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-16

@author: Jay
"""

from utest_lib.common import *
import unittest


class ServiceMgrServiceSelectTest(unittest.TestCase):

    # 初始化工作
    def setUp(self):
        pass

    # 退出清理工作
    def tearDown(self):
        pass

    @unittest_adaptor()
    def test_select_service_random(self):
        for _ in xrange(0, 10):
            service = random.choice(SERVICE_TYPE)
            if service == ST_SERVICE_MGR:
                continue
            pre_str = "%s find_service:" % service
            print pre_str + str(ServiceMgrCacher.find_service(service))

    @unittest_adaptor()
    def test_select_service_the_same(self):
        for _ in xrange(0, 5):
            service = random.choice(SERVICE_TYPE)
            if service == ST_SERVICE_MGR:
                continue
            rdm_str = random_str()
            self.assertTrue(str(ServiceMgrCacher.find_service(service, RT_HASH_RING, [rdm_str])) ==
                            str(ServiceMgrCacher.find_service(service, RT_HASH_RING, [rdm_str])) ==
                            str(ServiceMgrCacher.find_service(service, RT_HASH_RING, [rdm_str])) ==
                            str(ServiceMgrCacher.find_service(service, RT_HASH_RING, [rdm_str])) ==
                            str(ServiceMgrCacher.find_service(service, RT_HASH_RING, [rdm_str])))

    @unittest_adaptor()
    def test_select_service_the_same_multi(self):
        for _ in xrange(0, 5):
            service = random.choice(SERVICE_TYPE)
            if service == ST_SERVICE_MGR:
                continue
            rdm_str = random_str(str_len=10)
            self.assertTrue(str(ServiceMgrCacher.find_service(service, RT_HASH_RING, rdm_str)) ==
                            str(ServiceMgrCacher.find_service(service, RT_HASH_RING, rdm_str)) ==
                            str(ServiceMgrCacher.find_service(service, RT_HASH_RING, rdm_str)) ==
                            str(ServiceMgrCacher.find_service(service, RT_HASH_RING, rdm_str)) ==
                            str(ServiceMgrCacher.find_service(service, RT_HASH_RING, rdm_str)))
