#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-17

@author: Jay
"""
import random
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from utils.service_control.setting import is_logic_service, is_tp_service
from pandora.lib import get_pandora_info
from pandora.lib.service import ServiceViewer, ServicePuller


@route(r'/', name='Root')
class RootHandle(HttpRpcHandler):
    """
    根目录handler
    """
    @web_adaptor(use_http_render=False)
    def get(self):
        """
        http get 请求
        :return:
        """
        view_services, view_count = ServiceViewer().view_grp_service()
        view_tp_services, view_tp_count = ServiceViewer().view_tp_service()
        render_data = {'grp_service_dic': view_services,
                       'grp_count_dic': view_count,
                       'tp_service_dic': view_tp_services,
                       'tp_count_dic': view_tp_count,
                       'pandora_info': get_pandora_info()}
        self.render('view_service.html', **render_data)


@route(r'/services', name='services')
class ServicesHandle(HttpRpcHandler):
    """
    服务查询handler
    """
    @web_adaptor(use_http_render=False)
    def get(self, service=None):
        """
        http get 请求
        :return:
        """
        view_services, view_count = ServiceViewer().view_grp_service(service)
        view_tp_services, view_tp_count = ServiceViewer().view_tp_service(service)
        render_data = {'grp_service_dic': view_services,
                       'grp_count_dic': view_count,
                       'tp_service_dic': view_tp_services,
                       'tp_count_dic': view_tp_count,
                       'pandora_info': get_pandora_info()}
        self.render('view_service.html', **render_data)


@route(r'/locate', name='locate')
class LocateHandle(HttpRpcHandler):
    """
    服务定位处理器
    """
    @web_adaptor()
    def get(self, service):
        """
        http get 请求
        :return:
        """
        if not service:
            return {}

        all_services = ServicePuller().all_grp_services \
            if service and is_logic_service(service)  \
            else ServicePuller().all_tp_services

        if service not in all_services.keys():
            return {}

        validate_services = all_services[service]
        if not validate_services:
            return {}

        return random.choice(validate_services)['locate']


@route(r'/service_doc', name='service_doc')
class ServiceDocHandle(HttpRpcHandler):
    """
    服务文档查看处理器
    """
    @web_adaptor(use_json_dumps=False, use_http_render=False)
    def get(self, service):
        """
        http get 请求
        目前不支持第三方服务的文档
        :return:
        """
        if not service or is_tp_service(service):
            return ""

        all_services = ServicePuller().all_grp_services

        if service not in all_services.keys():
            return ""

        validate_services = all_services[service]
        if not validate_services:
            return ""

        return self.redirect(random.choice(validate_services)['href'])

