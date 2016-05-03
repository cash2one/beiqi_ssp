#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-26

@author: Jay
"""
import copy
import traceback
import ujson
from utils import logger
from utils.meta.singleton import Singleton
from utils.regex import IP_REGEX
from utils.meta.imanager import IManager
from utils.service_control.checker import PortChecker, MysqlChecker
from utils.service_control.setting import SS_FREE, SS_RUNNING, PT_TCP, TP_SERVICE_FLAG
from service_mgr.lib.filter_result import FilterResult

TPSERVICE_CHECK_INTERVAL = 120
TP_MYSQL = TP_SERVICE_FLAG+"mysql"

class TPService(PortChecker):
    def __init__(self, id, ip, service_group, port, params):
        self.id = id
        self.ip = ip
        self.service_group = service_group
        self.port = port
        self.params = params
        self.state = SS_RUNNING

        self.locate = dict((k, "%s:%s" % (self.ip, v)) for k, v in copy.deepcopy(self.port).items())

        super(TPService, self).__init__(self.port, self.ip, check_interval=TPSERVICE_CHECK_INTERVAL)
        super(TPService, self).start()

    def __del__(self):
        super(TPService, self).stop()

    def __str__(self):
        return str(self.__dict__)

    def _get_checker(self, type, port):
        if type.lower() == PT_TCP.lower():
            if self.service_group.lower() == TP_MYSQL.lower():
                return MysqlChecker(self.ip,
                                    port,
                                    "information_schema",
                                    self.params['db_user'],
                                    self.params['db_password'])
        return PortChecker._get_checker(type, port)

    def _on_disconnected(self, checker, since_connected):
        self._set_state(SS_FREE)

    def _on_connected(self):
        self._set_state(SS_RUNNING)

    def get_info_dic(self):
        return {"id": self.id,
                "ip": self.ip,
                "service_group": self.service_group,
                "port": self.port,
                "params": self.params,
                "locate": self.locate,
                "state": self.state}

    def _set_state(self, new_state):
        if new_state == self.state:
            return
        self.state = new_state


class TPServiceMgr(IManager):
    __metaclass__ = Singleton

    def __init__(self):
        self.tp_service_dic = {}
        self.init_data_ls = None

    def init(self, data_ls):
        self.init_data_ls = data_ls
        self.tp_service_dic = {}
        for dic in data_ls:
            self.tp_service_dic.setdefault(dic['service_group'], []).append(TPService(**dic))

    def get_init_data_ls(self):
        return self.init_data_ls

    def db_pick(self, data_ls):
        """
        db 序列化
        :param data_ls:
        :return:
        """
        pick_ls = copy.deepcopy(data_ls)
        for dic in pick_ls:
            dic["port"] = ujson.dumps(dic['port']) if dic['port'] else ""
            dic["params"] = ujson.dumps(dic['params']) if dic['params'] else ""
        return pick_ls

    def db_unpick(self, data_ls):
        """
        db 反序列化
        :param data_ls:
        :return:
        """
        un_pick_ls = copy.deepcopy(data_ls)
        for dic in un_pick_ls:
            dic["port"] = ujson.loads(dic['port']) if dic['port'] else {}
            dic["params"] = ujson.loads(dic['params']) if dic['params'] else {}
        return un_pick_ls

    def web_pick(self):
        """
        web 序列化
        :return:
        """
        data_ls = []
        [[data_ls.append(tp_service_obj.get_info_dic())
         for tp_service_obj in tp_service_ls]
         for _, tp_service_ls in self.tp_service_dic.items()]
        return self.db_pick(data_ls)

    def web_unpick(self, data_ls):
        """
        web 反序列化
        :param data_ls:
        :return:
        """
        unpick_ls = copy.deepcopy(data_ls)

        v_unpick_data_ls = []
        for data_dic in unpick_ls:
            try:
                data_dic['port'] = ujson.loads(data_dic['port']) if data_dic['port'] else {}
                data_dic['params'] = ujson.loads(data_dic['params']) if data_dic['params'] else {}

                if not data_dic['id']\
                        or not data_dic['service_group']\
                        or not IP_REGEX.match(data_dic['ip']) if data_dic['ip'] else False:
                    logger.warn("TPServiceMgr::web_unpick invalid params:%s" % data_dic)
                    continue
            except:
                logger.warn("TPServiceMgr::web_unpick invalid params:%s %s" % (data_dic, traceback.format_exc()))
                raise

            v_unpick_data_ls.append(data_dic)
        return v_unpick_data_ls

    def filter_tp_services(self, filter_result=FilterResult, service_grp_id=None):
        """
        根据服务器组名称帅选第三方服务列表
        :param filter_result:结果返回方式
        :param service:服务器组， 服务器id/服务器组列表
        :return: {"grp_id":[service_dic,,,],,,,,}
        """
        f_result = filter_result()

        if service_grp_id:
            if isinstance(service_grp_id, tuple):
                service_grp_id = list(service_grp_id)
            elif not isinstance(service_grp_id, list):
                service_grp_id = [service_grp_id]

        [f_result.form(t_service_grp_id, [tp_service_obj.get_info_dic() for tp_service_obj in tp_service_obj_ls])
         for t_service_grp_id, tp_service_obj_ls in self.tp_service_dic.items()
         if service_grp_id is None or t_service_grp_id in service_grp_id]

        return f_result.result()
