#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-26

@author: Jay
"""
import copy
import traceback
import random
import time
import ujson
from collections import defaultdict
from utils.meta.singleton import Singleton
from utils import logger
from utils.meta.imanager import IManager
from utils.comm_func import timestamp_to_string
from utils.service_control.setting import RT_HASH_RING, RT_CPU_USAGE_RDM, SS_RUNNING, SS_FREE, SERVICE_STATE
from service_mgr.lib.filter_result import FilterServiceDicKeyGrpResult, FilterResult
from service_cluster import ServiceCluster
from service_backup import ServiceBackup
from service_hb import ServiceHeartBeat
from service_ctl import ServiceCtl
from service_verify import ServiceVerify
from service_mgr.lib.service import ServiceComposeCtl


class Service(ServiceComposeCtl):
    def __init__(self, service_group, ip, port, jid):
        """
        初始化服务信息
        :param id:  服务id
        :param ip:  ip
        :param port:  端口，字典形式: {"tcp":xxx, "http":xxx, "https":xxx}
        :param service_group:
        :param jid:
        :return:
        """
        assert isinstance(port, dict)
        self.service_group = service_group
        self.ip = ip
        self.port = port
        self.jid = jid

        self.service_version = ""
        self.current_load = ""
        self.state = SS_FREE

        self.id = self.make_id(service_group, ip, port)
        self.start_time = time.time()

        self.__heartbeat_time = None

        super(Service, self).__init__()

    @staticmethod
    def make_id(service_group, ip, port):
        id = "%s%s%s" % (service_group, ip, "".join(str(v) for v in port.values()))
        id = id.replace("_", "").replace(".", "")
        return id

    @property
    def heartbeat_time(self):
        return self.__heartbeat_time

    @heartbeat_time.setter
    def heartbeat_time(self, new_hb_time):
        self.__heartbeat_time = new_hb_time

    def gen_view_info(self):
        is_https = 'https' in self.port
        http_proctol = "https" if is_https else "http"
        http_host = self.ip + ":" + str(self.port['https'] if is_https else self.port['http'])

        self.href_doc = http_host
        self.href = "%s://%s/doc" % (http_proctol, self.href_doc)
        self.locate = {http_proctol: http_host, "xmpp": "%s" % self.jid} \
            if self.jid \
            else {http_proctol: http_host}

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.id == other.id

    def get_info_dic(self):
        return {"id": self.id,
                "ip": self.ip,
                "service_group": self.service_group,
                "port": self.port,
                "jid": self.jid,
                "state": self.state,
                "start_time": timestamp_to_string(self.start_time),
                "heartbeat_time": timestamp_to_string(self.__heartbeat_time),
                "service_version": self.service_version,
                "current_load": self.current_load,
                "href_doc": self.href_doc,
                "href": self.href,
                "locate": self.locate}

    def web_pick(self):
        return {"id": self.id,
                "ip": self.ip,
                "service_group": self.service_group,
                "port": self.port,
                "jid": self.jid,
                "state": self.state,
                "start_time": timestamp_to_string(self.start_time),
                "heartbeat_time": timestamp_to_string(self.__heartbeat_time),
                "service_version": self.service_version,
                "current_load": self.current_load,
                "href_doc": self.href_doc if self.state == SS_RUNNING else "",
                "href": self.href if self.state == SS_RUNNING else ""}

    def _use(self):
        self.set_state(SS_RUNNING)

    def _free(self):
        if self.state == SS_FREE:
            return
        self.set_state(SS_FREE)

    def set_state(self, new_state):
        if new_state == self.state:
            return

        self.state = new_state

    def is_free(self):
        return self.state == SS_FREE

    def start(self):
        if not self.is_free():
            return False

        self._use()
        self.start_time = time.time()
        self.start_cp()
        ServiceMgr().add_service(self)
        return True

    def stop(self):
        if not self.state == SS_RUNNING:
            return True

        self._free()
        self.stop_cp()
        ServiceMgr().del_service(self)
        return True

    def hash_key(self):
        return self.id



class ServiceMgr(IManager):
    __metaclass__ = Singleton

    def __init__(self):
        self.__id_to_service_dic = {}
        self.__state_service_dic = {}
        ServiceCluster.service_mgr = self
        self.__grp_srv_cluster = defaultdict(ServiceCluster)
        self.__init_data_ls = None

    def new_service(self, service_group, ip, port, jid):
        service_obj = Service(service_group, ip, port, jid)
        service_obj.add_cp(ServiceHeartBeat(service_obj))
        service_obj.add_cp(ServiceCtl(service_obj))
        service_obj.add_cp(ServiceVerify(service_obj))

        # 如果是xxx_da的服务，才需要做备份
        if "da" in service_group:
            service_obj.add_cp(ServiceBackup(service_obj))
        service_obj.start()
        return service_obj

    def add_service(self, service_obj):
        """
        添加一个服务对象
        :param service_obj:
        :return:
        """
        assert service_obj.state == SS_RUNNING
        # id_to_service_dic
        self.__id_to_service_dic[service_obj.id] = service_obj

        # state_service_dic
        self.__state_service_dic.setdefault(service_obj.service_group, {})\
            .setdefault(service_obj.ip, {})\
            .setdefault(SS_RUNNING, {})[service_obj.hash_key()] = service_obj

        # running_hash_ring
        self.__grp_srv_cluster[service_obj.service_group].add_service(service_obj, is_init=True)

    def del_service(self, service_obj):
        """
        删除一个服务对象
        :param service_obj:
        :return:
        """
        assert service_obj.state == SS_FREE
        # id_to_service_dic
        self.__id_to_service_dic.pop(service_obj.id, None)

        # state_service_dic
        self.__state_service_dic.get(service_obj.service_group, {})\
            .get(service_obj.ip, {})\
            .get(SS_RUNNING, {})\
            .pop(service_obj.hash_key(), None)

        # running_hash_ring
        self.__grp_srv_cluster[service_obj.service_group].del_service(service_obj)

    def update(self, curtime):
        [service_obj.update(curtime) for service_obj in self.__id_to_service_dic.values()]

    def get_init_data_ls(self):
        return self.__init_data_ls

    def json_pick(self, data_ls):
        """
        json 序列化
        :param data_ls:
        :return:
        """
        pick_ls = copy.deepcopy(data_ls)
        for dic in pick_ls:
            dic["port"] = ujson.dumps(dic['port']) if dic['port'] else ""
        return pick_ls

    def json_unpick(self, data_ls):
        """
        json 反序列化
        :param data_ls:
        :return:
        """
        un_pick_ls = copy.deepcopy(data_ls)
        for dic in un_pick_ls:
            dic["port"] = ujson.loads(dic['port']) if dic['port'] else {}
        return un_pick_ls

    def web_pick(self, service_grp=None):
        """
        web 序列化
        :return:
        """
        grp_services = self.filter_services(FilterServiceDicKeyGrpResult, service_grp, None, None)
        [grp_services.update({grp: self.json_pick(services)}) for grp, services in grp_services.items()]
        grp_counts = dict((grp, len(services)) for grp, services in grp_services.items())
        return grp_services, grp_counts

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
                data_dic["port"] = ujson.loads(data_dic['port']) if data_dic['port'] else {}
                data_dic["params"] = ujson.loads(data_dic['params']) if data_dic['params'] else {}
                data_dic['state'] = SS_RUNNING if data_dic['state'] == "连接" else SS_FREE

                if not data_dic['service_group'] \
                        or not int(data_dic['state']) in SERVICE_STATE:
                    logger.warn("ServiceMgr::web_unpick invalid params:%s" % data_dic)
                    continue

                # 去除临时数据
                del data_dic['process_name']
                del data_dic['service_version']
                del data_dic['current_load']
                del data_dic['heartbeat_time']
            except:
                logger.warn("ServiceMgr::web_unpick invalid params:%s %s" % (data_dic, traceback.format_exc()))
                raise

            v_unpick_data_ls.append(data_dic)
        return v_unpick_data_ls

    def get_service_by_id(self, service_id):
        return self.__id_to_service_dic.get(service_id, None)

    def get_services_by_hash_keys(self, hash_keys):
        return [self.get_service_by_id(hash_key) for hash_key in hash_keys]

    def get_run_services(self, service_grp_id, rdm_type=RT_CPU_USAGE_RDM, rdm_param=1):
        """
        选择在线服务列表
        注意，由于是列表操作，所以返回的对象有可能为空
        :param service_grp_id:服务组id
        :param rdm_type: 随机类型
        :param rdm_param: 随机参数，RT_HASH_RING:列表, RT_RANDOM:整形，随机个数
        :return:[Obj,Obj,Obj,,,]
        """
        if rdm_type == RT_HASH_RING:
            if not isinstance(rdm_param, list):
                rdm_param = [rdm_param]
            return self.__grp_srv_cluster[service_grp_id].get_service_objs(rdm_param)
        else:
            running_hash_keys = []
            [running_hash_keys.extend(machine_state_dic.get(SS_RUNNING, {}).keys())
             for machine_state_dic in self.__state_service_dic.get(service_grp_id, {}).values()]
            selected_hash_keys = random.sample(running_hash_keys, int(rdm_param)) if running_hash_keys else []
            return self.get_services_by_hash_keys(selected_hash_keys)

    def filter_services(self, filter_result=FilterResult, service_grp_id=None, ip=None, state=None):
        """
        根据服务器组、IP和状态筛选满足条件的服务
        :param filter_result:结果返回方式
        :param service_grp_id: 服务器组/服务器组列表
        :param ip: IP/IP列表
        :param state:服务状态
        :return:
        """
        f_result = filter_result()

        if isinstance(service_grp_id, tuple):
            service_grp_id = list(service_grp_id)
        elif service_grp_id is not None and not isinstance(service_grp_id, list):
            service_grp_id = [service_grp_id]

        if isinstance(ip, tuple):
            ip = list(ip)
        elif ip is not None and not isinstance(ip, list):
            ip = [ip]

        [[[f_result.form(t_service_grp_id, t_ip, t_state, id_service_dic)
           for t_state, id_service_dic in state_service_dic.items()
           if state is None or t_state == state]
          for t_ip, state_service_dic in ip_service_dic.items()
          if ip is None or t_ip in ip]
         for t_service_grp_id, ip_service_dic in self.__state_service_dic.items()
         if service_grp_id is None or t_service_grp_id in service_grp_id]

        return f_result.result()