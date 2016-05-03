#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-20

@author: Jay
"""
import copy
from utils.comm_func import sub_dict
from utils.scheduler import Jobs
from utils.service_control.cacher import ParamCacher
from utils.meta.singleton import Singleton
from utils.service_control.setting import SS_RUNNING
from utils.wapper.catch import except_adaptor
from utils.wapper.stackless import gevent_adaptor
from interfaces.service_mgr.tcp_rpc import view_logic_services, view_tp_services
from pandora.setting import SERVICE_TYPE as ST_PANDORA

SERVICE_FRESH_INTERVAL = 12


class ServicePuller(object):
    """
    服务获取管理器
    """
    __metaclass__ = Singleton

    def __init__(self):
        self.all_grp_services = {}
        self.all_tp_services = {}
        self.pull()

    def start(self):
        """
        开启工作
        :return:None
        """
        Jobs().add_interval_job(SERVICE_FRESH_INTERVAL, self.pull)

    @gevent_adaptor(use_join_result=False)
    @except_adaptor()
    def pull(self):
        """
        拉取数据
        :return:None
        """
        self.all_grp_services = view_logic_services(ParamCacher().sm_rpc, ST_PANDORA, SS_RUNNING)
        self.all_tp_services = view_tp_services(ParamCacher().sm_rpc, ST_PANDORA)

class ServiceViewer(object):
    """
    服务查看管理器
    """
    __metaclass__ = Singleton

    @staticmethod
    def view_grp_service(service_grp=None):
        """
        查看逻辑服务
        :param service_grp:逻辑服务组
        :return:服务字典, 服务个数字典
        """
        all_grp_services = ServicePuller().all_grp_services

        if service_grp and service_grp not in all_grp_services.keys():
            return {}, {}

        view_grp_services = sub_dict(all_grp_services, [service_grp]) if service_grp else all_grp_services

        view_services = {}
        for grp, grp_service in view_grp_services.items():
            for service in grp_service:
                copy_service = copy.deepcopy(service)
                view_services.setdefault(grp, []).append(copy_service)

        view_count_dic = dict((grp, len(grp_service)) for grp, grp_service in view_services.items())
        return view_services, view_count_dic

    @staticmethod
    def view_tp_service(tp_name=None):
        """
        查看第三方服务
        :param tp_name:第三方服务名称
        :return:服务字典, 服务个数字典
        """
        all_tp_services = ServicePuller().all_tp_services

        if tp_name and tp_name not in all_tp_services.keys():
            return {}, {}

        viewed_services = sub_dict(all_tp_services, [tp_name]) if tp_name else all_tp_services

        viewed_count_dic = dict((tp, len(tp_services)) for tp, tp_services in viewed_services.items())
        return viewed_services, viewed_count_dic
