#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-14

@author: Jay
"""
from lib.common import *
from utils.hash_ring import HashRing
from utils.comm_func import random_str

class HashRingTest(unittest.TestCase):

    # 初始化工作
    def setUp(self):
        pass

    # 退出清理工作
    def tearDown(self):
        pass

    @unittest_adaptor()
    def test_hashring1(self):
        memcache_servers = ['192.168.0.246:11212',
                            '192.168.0.247:11212',
                            '192.168.0.249:11212']

        ring = HashRing(memcache_servers)
        my_key = "zhanchenjinssssss"
        self.assertTrue(ring.get_node(my_key) ==
                        ring.get_node(my_key) ==
                        ring.get_node(my_key) ==
                        ring.get_node(my_key))

        my_key = "gggggggggggggg"
        self.assertTrue(ring.get_node(my_key) ==
                        ring.get_node(my_key) ==
                        ring.get_node(my_key) ==
                        ring.get_node(my_key))

    @unittest_adaptor()
    def test_hashring2(self):
        memcache_servers1 = ['192.168.0.246:11212',
                            '192.168.0.247:11212',
                            '192.168.0.249:11212',
                            '192.168.0.250:11212',
                            '192.168.0.251:11212',
                            '192.168.0.252:11212',
                            '192.168.0.253:11212',
                            '192.168.0.254:11212',
                            '192.168.0.255:11212',
                            '192.168.0.256:11212']

        ring1 = HashRing(memcache_servers1)
        my_key = "zhanchenjinssssss"
        ring1.get_node("aaaa")
        my_value1 = ring1.get_node(my_key)

        memcache_servers2 = ['192.168.0.246:11212',
                            '192.168.0.247:11212',
                            '192.168.0.249:11212',
                            '192.168.0.250:11212',
                            '192.168.0.251:11212',
                            '192.168.0.252:11212',
                            '192.168.0.253:11212',
                            '192.168.0.254:11212',
                            '192.168.0.255:11212',
                            '192.168.0.256:11212']

        ring2 = HashRing(memcache_servers2)
        ring2.get_node("aaaa")
        my_value2 = ring2.get_node(my_key)
        self.assertTrue(my_value1 == my_value2)
    @unittest_adaptor()
    def test_hashring_none(self):
        ring1 = HashRing([])
        my_key = "zhanchenjinssssss"
        self.assertTrue(ring1.get_node(my_key) == None)

    @unittest_adaptor()
    def test_hashring_next_nodes(self):
        """
    判断某个节点删除以后，HashRing给某个相同字符串的定位节点是否和HashRing的next_nodes函数取得的节点一致
        """

        memcache_servers = ['192.168.0.246:11212',
                            '192.168.0.247:11212',
                            '192.168.0.248:11212',
                            '192.168.0.249:11212']

        text_cont = 30
        for i in xrange(text_cont):
            ring = HashRing(memcache_servers, replicas=1)

            test_str = random_str(i)

            select_node = ring.get_node(test_str)
            next_nodes = ring.next_nodes(select_node)
            ring.remove_node(select_node)
            reselect_node = ring.get_node(test_str)
            self.assertTrue(reselect_node in next_nodes)

    @unittest_adaptor()
    def test_hashring_self_next_node(self):
        """
    判断是否有屏蔽到自己的下一个节点
        """

        memcache_servers = ['192.168.0.246:11212']

        ring = HashRing(memcache_servers, replicas=1)
        test_str = random_str()

        select_node = ring.get_node(test_str)
        next_nodes = ring.next_nodes(select_node)
        self.assertTrue(not next_nodes)

    @unittest_adaptor()
    def test_hashring_has_node(self):
        """
    判断是否有节点
        """

        memcache_servers = ['192.168.0.246:11212']

        ring = HashRing(memcache_servers, replicas=1)
        self.assertTrue(ring.has_node('192.168.0.246:11212'))

        new_node = '192.168.0.247:11212'
        ring.add_node(new_node)
        self.assertTrue(ring.has_node(new_node))

        ilexist_node = '192.168.0.248:11212'
        self.assertTrue(not ring.has_node(ilexist_node))
