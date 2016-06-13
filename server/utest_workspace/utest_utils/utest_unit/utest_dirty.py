#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-6-1

@author: Jay
"""
from utest_lib.common import *
from utils.data.cache.dirty import DirtyFlag, DirtyDictProcess, DirtyFlagProcess, DB_OPER_TYPE_INSERT, DB_OPER_TYPE_DELETE, DB_OPER_TYPE_UPDATE


g_args = None
g_kwargs = None

def client_dirty_receive_fun(*args, **kwargs):
    global g_args, g_kwargs
    g_args = args
    g_kwargs = kwargs

class DrityTest(unittest.TestCase):

    # 初始化工作
    def setUp(self):
        logger.init_log("TCPRPCTest", "TCPRPCTest")

    # 退出清理工作
    def tearDown(self):
        pass

    @unittest_adaptor()
    def test_dirty_flag(self):
        # add_flag测试
        df = DirtyFlag()
        df.add_flag('k1')
        self.assertTrue(df.get_all_keys() == set(['k1']))
        self.assertTrue(df.get_dirty_keys() == set(['k1']))

        # add_flag_set测试
        df.add_flag_set(['k2','k3'])
        self.assertTrue(df.get_all_keys() == set(['k1','k2','k3']))
        self.assertTrue(df.get_dirty_keys() == set(['k1','k2', 'k3']))

        # reset_flags测试
        df.reset_flags(False)
        self.assertTrue(df.get_dirty_keys() == set([]))
        df.reset_flags(True)
        self.assertTrue(df.get_dirty_keys() == set(['k1','k2', 'k3']))

        # del_flag测试
        df.del_flag('k2')
        self.assertTrue(df.get_dirty_keys() == set(['k1','k3']))

        # del_all_flag测试
        df.del_all_flag()
        self.assertTrue(df.get_dirty_keys() == set([]))

    @unittest_adaptor()
    def test_dirty_flag_process(self):
        client_key = 'role_attr'
        test_args = [1, 2, 3, 4, 5, 6]
        test_kwargs = {'2': 3, '4': 5, '7': 90}

        class DirtyClass:
            def __init__(self, role_id):
                self.db_key = role_id
                self.DirtyFlag = DirtyFlagProcess(self)
                self.DirtyFlag.add_dirty_notify_fun(client_dirty_receive_fun, *test_args, **test_kwargs)

            def update(self):
                self.dirty_dic = self.DirtyFlag.get_client_dirty_attr()

            def get_dirty(self):
                return self.db_key, self.dirty_dic

            def set_k1(self, v):
                self.k1 = v
                self.DirtyFlag.add_flag('k1')

            def get_k1(self):
                return self.k1

            def set_k2(self, v):
                self.k2 = v
                self.DirtyFlag.add_flag('k2')

            def get_k2(self):
                return self.k2

            def set_k3(self, v):
                self.k3 = v
                self.DirtyFlag.add_flag('k3')

            def get_k3(self):
                return self.k3

            def reset_client_flags(self, reset_value):
                self.DirtyFlag.reset_client_flags(reset_value)

            def get_client_dirty_attr(self):
                dirty_dict = self.DirtyFlag.get_client_dirty_attr()
                return {client_key:dirty_dict} if dirty_dict else {}

        # 1 value get_client_dirty_attr
        dbkey = 100
        dc = DirtyClass(dbkey)
        vk1 = 'test1'
        dc.set_k1(vk1)
        self.assertTrue(dc.get_client_dirty_attr() == {client_key: {'k1': vk1}})

        # 3 value get_client_dirty_attr
        vk2 = 'test2'
        dc.set_k2(vk2)
        vk3 = 'test3'
        dc.set_k3(vk3)
        self.assertTrue(dc.get_client_dirty_attr() == {client_key: {'k2': vk2, 'k3': vk3}})

        # reset_client_flags
        dc.reset_client_flags(True)
        self.assertTrue(dc.get_client_dirty_attr() == {client_key: {'k1': vk1, 'k2': vk2, 'k3': vk3}})

        dc.reset_client_flags(False)
        self.assertTrue(dc.get_client_dirty_attr() == {})

        # test export func
        dbkey = 101
        db_export = DirtyClass(dbkey)
        vk2 = 'sssssssssssssss'
        db_export.set_k2(vk2)
        db_export.update()
        dirty_db_key, dirty_db_dict = db_export.get_dirty()
        self.assertTrue(dirty_db_key == dbkey)
        self.assertTrue(dirty_db_dict == {'k2': vk2})

        # test client_dirty_notify
        self.assertTrue(list(g_args) == test_args)
        self.assertTrue(g_kwargs == test_kwargs)

    @unittest_adaptor()
    def test_dirty_dict_process(self):
        logic_flag = "test"
        db_table = "testdb"
        key_ls = ["p1", "p2"]
        role_id = 100

        class DirtyDictClass:
            def __init__(self):
                self.DirtyDictProcess = DirtyDictProcess(key_ls)

        ddc = DirtyDictClass()

        # 客户端测试
        role_id1 = 100
        k1 = 'k1'
        vk1 = 'test1'
        vdict1 = {"p1": 1, "p2": 2, k1: vk1}
        ddc.DirtyDictProcess.ist_client_dict(role_id, vdict1)
        k2 = 'k2'
        vk2 = 'test2'
        vdict2 = {"p1": 1, "p2": 2, k2: vk2}
        ddc.DirtyDictProcess.del_client_dict(role_id, vdict2)
        k3 = 'k3'
        vk3 = 'test3'
        vdict3 = {"p1": 1, "p2": 2, k3: vk3}
        ddc.DirtyDictProcess.upd_client_dict(role_id, vdict3)
        dirty_dict = ddc.DirtyDictProcess.get_client_dirty_dict(role_id)
        print "dirty_dict,",dirty_dict

        vdict1.update(vdict3)
        should_vdict1 = vdict1
        should_dict = {'upd': [should_vdict1],
                       'del': [{'p1': vdict2['p1'], 'p2': vdict2['p2']}]}
        print "should_dict，",should_dict
        self.assertTrue(dirty_dict == should_dict)

        # db 测试1, 简单插入测试
        ddc = DirtyDictClass()
        ddc.DirtyDictProcess.ist_db_dict(role_id, vdict1)
        db_dirty= ddc.DirtyDictProcess.get_db_dirty_dict(role_id)
        self.assertTrue(db_dirty == {DB_OPER_TYPE_INSERT: [vdict1]})

        # db 测试1, 简单upd测试
        ddc = DirtyDictClass()
        ddc.DirtyDictProcess.upd_db_dict(role_id, vdict1)
        db_dirty= ddc.DirtyDictProcess.get_db_dirty_dict(role_id)
        self.assertTrue(db_dirty == {DB_OPER_TYPE_UPDATE: [vdict1]})

        # db 测试1, 抵消测试
        ddc = DirtyDictClass()
        ddc.DirtyDictProcess.ist_db_dict(role_id, vdict1)
        ddc.DirtyDictProcess.upd_db_dict(role_id, vdict3)
        ddc.DirtyDictProcess.del_db_dict(role_id, vdict2)

        db_dirty = ddc.DirtyDictProcess.get_db_dirty_dict(role_id)
        self.assertTrue(db_dirty == {})

        # db 测试1, upd更新ist测试
        ddc = DirtyDictClass()
        vdict1 = {"p1": 1, "p2": 2, k1: vk1}
        vdict2 = {"p1": 1, "p2": 2, k1: vk2}
        ddc.DirtyDictProcess.ist_db_dict(role_id, vdict1)
        ddc.DirtyDictProcess.upd_db_dict(role_id, vdict2)

        db_dirty = ddc.DirtyDictProcess.get_db_dirty_dict(role_id)
        self.assertTrue(db_dirty == {DB_OPER_TYPE_INSERT:[vdict2]})

