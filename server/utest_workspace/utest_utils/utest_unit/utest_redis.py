#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-15

@author: Jay
"""
from lib.common import *


rc = redis_client.RedisClient(REDIS_IP, REDIS_PORT, pwd=REDIS_PASSWD)

testk = 'test'
testv = 'v'
test1k = 'test1'
test1v = 'v1'
test2k = 'test2'
test2v = 'v2'
tmpv = '1111111'


class RedisTest(unittest.TestCase):

    # 初始化工作
    def setUp(self):
        pass

    # 退出清理工作
    def tearDown(self):
        cmds = [['delete', testk, test1k, test2k]]
        self.assertTrue(rc.pipe_execute(cmds))

    @unittest_adaptor()
    def test_set_get(self):
        rc.set(testk, testv)
        self.assertTrue(rc.get(testk) == testv)

    @unittest_adaptor()
    def test_del(self):
        rc.set(testk, testv)
        self.assertTrue(rc.delete(testk, '1'))

    @unittest_adaptor()
    def test_expire(self):
        exp_time = 1
        rc.set(testk, testv)
        rc.expire(testk, exp_time)
        self.assertTrue(rc.get(testk) == testv)
        time.sleep(exp_time+1)
        self.assertTrue(rc.get(testk) is None)

    @unittest_adaptor()
    def test_execute(self):
        rc.execute(['set', test1k, test1v])
        self.assertTrue(rc.execute(['get', test1k]) == test1v)

    @unittest_adaptor()
    def test_pip_execute(self):
        cmds = [['set', test2k, test2v],
                ['set', test2k, tmpv],
                ['get', test2k]]
        self.assertTrue(rc.pipe_execute(cmds)[2] == tmpv)

    @unittest_adaptor()
    def test_pip_execute_expire(self):
        exp_sec = 1
        cmds = [['set', test2k, test2v, 10],
                ['set', test2k, tmpv, exp_sec],
                ['get', test2k]]
        self.assertTrue(rc.pipe_execute(cmds)[2] == tmpv)
        time.sleep(exp_sec+1)
        get_cmds = [['get', test2k]]
        self.assertTrue(rc.pipe_execute(get_cmds)[0] is None)
