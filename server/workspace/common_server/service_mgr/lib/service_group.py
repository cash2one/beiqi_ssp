#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-26

@author: Jay
"""
import copy
from utils.meta.singleton import Singleton
from utils import logger
from utils.meta.imanager import IManager

class ServiceGrp:
    def __init__(self, id):
        self._id = id

    @property
    def id(self):
        return self._id


class ServiceGrpMgr(IManager):
    __metaclass__ = Singleton

    def __init__(self):
        self.id_to_dic = {}
        self.type_to_dic = {}
        self.init_data_ls = None

    def add_grp(self, grp_obj):
        self.id_to_dic[grp_obj.id] = grp_obj

    def add_grp_id(self, grp_id):
        if not self.get_service_grp(grp_id):
            self.add_grp(ServiceGrp(grp_id))

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

        v_data_ls = []
        for data_dic in unpick_ls:
            if not data_dic['id']:
                logger.warn("ServiceGrpMgr::web_unpick invalid params:%s" % data_dic)
                continue
            v_data_ls.append(data_dic)
        return v_data_ls

    def get_service_grp(self, service_grp_id):
        return self.id_to_dic.get(service_grp_id, {})

    def get_service_grps(self):
        return self.id_to_dic.keys()
