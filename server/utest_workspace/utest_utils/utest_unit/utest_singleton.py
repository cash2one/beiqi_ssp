# coding=utf-8
"""
Created on 2015-4-22

@author: Jay
"""

from lib.common import *


class Test():
    __metaclass__ = Singleton

    def __init__(self):
        pass


class SingletonTest(unittest.TestCase):

    # 初始化工作
    def setUp(self):
        pass

    # 退出清理工作
    def tearDown(self):
        pass

    @unittest_adaptor()
    def test_attr(self):
        one = Test()
        two = Test()

        one.a = 1
        two.a = 2
        self.assertEqual(one.a,two.a)
        self.assertTrue(one.a == 2)
        self.assertFalse(two.a == 1)