#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-8-17

@author: Jay
"""
from utils import logger
from utils.meta.singleton import Singleton
from utils.network.http import HttpRpcClient
from utils.setting.wechat import MENU_CREATE_URL, MENU_GET_URL
from utils.wechat.ierror import WXBizMsgCrypt_OK
from service_mgr.lib.lib_wechat.access_token import CltAccessTokenGetter


class MenuManager(object):
    __metaclass__ = Singleton

    def __init__(self):
        pass

    def create_menu(self, menu):
        assert menu
        result = eval(HttpRpcClient(ssl=True).fetch_async(url=MENU_CREATE_URL(CltAccessTokenGetter().access_token),
                                                          body=menu))
        assert result['errcode'] == WXBizMsgCrypt_OK, result
        logger.warn("MenuManager::create_menu!!!!!!!!!!! new wechat menu:%s" % menu)

    def get_menu(self):
        return eval(HttpRpcClient(ssl=True).fetch_async(url=MENU_GET_URL(CltAccessTokenGetter().access_token)))