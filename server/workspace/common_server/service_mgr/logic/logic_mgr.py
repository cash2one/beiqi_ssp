#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-29

@author: Jay
"""
import time
from utils.meta.imanager import IManager
from utils.meta.singleton import Singleton
from service_mgr.db.db_oper import DBTpServiceInst,  DBWechatInst
from service_mgr.lib.tp_service import TPServiceMgr
from service_mgr.lib.wechat import WechatMgr


# 系统逻辑管理器列表
G_LOGIC_MANAGER_LIST = [(TPServiceMgr, DBTpServiceInst), 
                        (WechatMgr, DBWechatInst)
                        ]



class LogicMgr(IManager):
    __metaclass__ = Singleton

    def __init__(self):
        self.cur_time = time.time()

    def init(self, reload_db=False):
        """
        逻辑系统初始化
        @param reload_db:是否重新加载db
        """
        [mgr_info[0]().init(mgr_info[0]().db_unpick(mgr_info[1].query_all())) for mgr_info in G_LOGIC_MANAGER_LIST]

    def update(self, cur_time):
        """
        逻辑系统更新
        @param curtime:当前时间戳
        """
        [mgr_info[0]().update(cur_time) for mgr_info in G_LOGIC_MANAGER_LIST]
