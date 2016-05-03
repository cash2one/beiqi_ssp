#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016-4-7

@author: Jay
"""
class IManager(object):
    """
    管理器接口
    """
    def init_sql(self):
        return None

    def init(self, *args):
        pass

    def update(self, curtime):
        pass

    def destroy(self):
        pass

    def reload(self):
        pass

    def revert(self):
        pass

    def save_db(self, join = False):
        pass

    def db_pick(self, *args):
        """
        db 序列化
        :param data_ls:
        :return:
        """
        return {}

    def db_unpick(self, data_ls, *args):
        """
        db 反序列化
        :param data_ls:
        :return:
        """
        return data_ls

    def web_pick(self):
        """
        web 序列化
        :return:
        """
        return {}

    def web_unpick(self, data_ls):
        """
        web 反序列化
        :param data_ls:
        :return:
        """
        return data_ls