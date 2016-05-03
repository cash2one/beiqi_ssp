#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-27

@author: Jay
"""
import random
from utils import logger
from utils.network.tcp import TcpRpcHandler
from utils.wapper.stackless import gevent_adaptor
from utils.wapper.tcp import tcp_recv_adaptor, tcp_send_adaptor
from utils.wapper.crypto import sign_checker
from utils.service_control.setting import RT_CPU_USAGE_RDM, RT_HASH_RING
from service_mgr.lib.service.service_main import ServiceMgr
from service_mgr.lib.service_group import ServiceGrpMgr
from service_mgr.lib.tp_service import TPServiceMgr
from service_mgr.lib.filter_result import FilterServiceDicKeyGrpResult, \
    FilterTPServiceNotKeyResult, FilterTPServiceKeyGrpResult
from service_mgr.lib.lib_wechat.access_token import CltAccessTokenGetter, UserAuthInfoGetter


class TcpHandler(TcpRpcHandler):
    @gevent_adaptor()
    @tcp_send_adaptor()
    @tcp_recv_adaptor()
    @sign_checker()
    def find_service(self, service_type, rdm_type=RT_CPU_USAGE_RDM, rdm_param=1):
        """
        查找对应一个服务
        :param service_type:服务类型
        :param rdm_type:随机类型，0选择cpu使用率最低的；1一致性hash选择
        :param rdm_param:如果随机类型是0,参数整形,表示随机个数
                         如果随机类型是1,list形式,hash key 列表
        :return:
        """
        if rdm_type == RT_HASH_RING and not isinstance(rdm_param, list):
            rdm_param = [rdm_param]

        if not ServiceGrpMgr().get_service_grp(service_type):
            logger.error("TcpHandler::find_service Failed!!!, ERROR_PARAMS_ERROR, service_type:%s" % service_type)
            return {}

        service_obj_ls = ServiceMgr().get_run_services(service_type, rdm_type, rdm_param)
        if not service_obj_ls:
            return {}

        select_service_obj = service_obj_ls[0]
        if not select_service_obj:
            return {}

        return {"ip": select_service_obj.ip,
                "port": select_service_obj.port,
                "jid": select_service_obj.jid}

    @gevent_adaptor()
    @tcp_send_adaptor()
    @tcp_recv_adaptor()
    @sign_checker()
    def find_services(self, service_type, rdm_type=RT_CPU_USAGE_RDM, rdm_param=1):
        """
        查找服务列表
        :param service_type:服务类型
        :param rdm_type:随机类型，0选择cpu使用率最低的；1一致性hash选择
        :param rdm_param:如果随机类型是0,参数整形,表示随机个数
                         如果随机类型是1,list形式,hash key 列表
        :return:
        """
        if rdm_type == RT_HASH_RING and not isinstance(rdm_param, list):
            rdm_param = [rdm_param]

        if not ServiceGrpMgr().get_service_grp(service_type):
            logger.error("TcpHandler::find_service Failed!!!, ERROR_PARAMS_ERROR, service_type:%s" % service_type)
            return {}

        service_obj_ls = ServiceMgr().get_run_services(service_type, rdm_type, rdm_param)
        if not service_obj_ls:
            return {}

        result = {}
        for idx, service_obj in enumerate(service_obj_ls):
            result_key = idx if rdm_type == RT_CPU_USAGE_RDM else rdm_param[idx]
            result[result_key] = {"ip": service_obj.ip,
                                  "port": service_obj.port,
                                  "jid": service_obj.jid}
        return result

    @gevent_adaptor()
    @tcp_send_adaptor()
    @tcp_recv_adaptor()
    @sign_checker()
    def find_tp_service(self, service):
        """
        查找一个资源:
        :param service:第三方服务名称
        :return:
        """
        # 注意：此函数需要集群处理
        all_tp_service_ls = TPServiceMgr().filter_tp_services(FilterTPServiceNotKeyResult, service)
        return random.choice(all_tp_service_ls) if all_tp_service_ls else None

    @gevent_adaptor()
    @tcp_send_adaptor()
    @tcp_recv_adaptor()
    @sign_checker()
    def view_logic_services(self, viewer, state=None):
        """
        获取所有的服务，以group分组
        :param viewer: 请求者
        :param state: 需要的服务状态
        :return: {"grp":[service,,,,,],,,,}
        """
        return ServiceMgr().filter_services(FilterServiceDicKeyGrpResult,
                                            ServiceGrpMgr().get_service_grps(),
                                            None,
                                            state)

    @gevent_adaptor()
    @tcp_send_adaptor()
    @tcp_recv_adaptor()
    @sign_checker()
    def view_tp_services(self, viewer):
        """
        获取tp服务组信息
        :param viewer: 请求者
        :return: {"grp":[service,,,,,],,,,}
        """
        return TPServiceMgr().filter_tp_services(FilterTPServiceKeyGrpResult)

    @gevent_adaptor()
    @tcp_send_adaptor()
    @tcp_recv_adaptor()
    @sign_checker()
    def get_wc_clt_access_token(self):
        """
        获取微信客户端访问码
        :return: access_token
        """
        return CltAccessTokenGetter().access_token

    @gevent_adaptor()
    @tcp_send_adaptor()
    @tcp_recv_adaptor()
    @sign_checker()
    def get_wc_openid(self, code):
        """
        根据code获取微信用户openid
        :return: openid
        """
        return UserAuthInfoGetter().get_openid(code)
