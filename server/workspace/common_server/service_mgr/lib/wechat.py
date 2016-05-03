#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-8-18

@author: Jay
"""
import ujson
import copy
import re
from utils.meta.singleton import Singleton
from utils.meta.imanager import IManager
from utils.setting.wechat import GEN_WECHAT_REDIRECT_URL
from service_mgr.lib.lib_wechat.access_token import CltAccessTokenGetter


class WechatMgr(IManager):
    __metaclass__ = Singleton

    def __init__(self):
        CltAccessTokenGetter()
        self.data_dic = {}
        self.init_data_ls = None

    def init(self, data_ls):
        self.init_data_ls = data_ls
        self.data_dic = {}
        for setting_dic in data_ls:
            self.data_dic[setting_dic["k"]] = setting_dic

    def get_init_data_ls(self):
        return self.init_data_ls

    def db_unpick(self, data_ls):
        """
        db 反序列化
        :param data_ls:
        :return:
        """
        return data_ls

    def web_unpick(self, data_ls):
        """
        web 反序列化
        :param data_ls:
        :return:
        """

        unpick_ls = copy.deepcopy(data_ls)
        for data_dic in unpick_ls:
            for key, value in data_dic.items():
                data_dic[key] = str(ujson.loads(value))
        return unpick_ls

    def web_pick(self):
        """
        web 序列化
        :return:
        """
        pick_ls = copy.deepcopy(self.data_dic.values())
        for data_dic in pick_ls:
            for key, value in data_dic.items():
                data_dic[key] = ujson.dumps(value)
        return pick_ls

    def get_value(self, key):
        return self.data_dic.get(key, None).get("v", None)

    def gen_menu_str(self):
        """
        获取当前的菜单字符串
        :return:
        """
        wechat_menu = self.get_value("wechat_menu")
        wechat_cb_domain = self.get_value("wechat_cb_domain")
        assert wechat_menu
        assert wechat_cb_domain

        # 将%URL/device_ls% 字符串替换成wechat_controller重定向URL
        url_replace_regex = re.compile(r"%[^%]*%")
        url_str_ls = url_replace_regex.findall(wechat_menu)
        for url_str in url_str_ls:
            url_fun = url_str.replace("%", "").split("URL/")[1]
            cb_url = GEN_WECHAT_REDIRECT_URL("http://%s/%s" % (wechat_cb_domain, url_fun))
            wechat_menu = wechat_menu.replace(url_str, cb_url).replace("\'", "\"")
        return wechat_menu
