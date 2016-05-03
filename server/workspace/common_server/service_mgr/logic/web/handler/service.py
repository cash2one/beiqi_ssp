# coding=utf-8
"""
Created on 2015-4-22

@author: Jay
"""
import traceback
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor, ajax_recv_wapper
from service_mgr.logic.web import setting as web_setting
from service_mgr.logic.web import require_login
from service_mgr.lib.service.service_main import ServiceMgr


@route(r'/service_manager', name='service_manager')
class ServiceManager(HttpRpcHandler):
    """
    服务管理
    """
    @require_login
    @web_adaptor(use_http_render=False)
    def get(self, *args, **kwargs):
        render_dict = {'func_list': web_setting.service_manager}
        self.render('main.html', **render_dict)


@route(r'/view_all_service', name='view_all_service')
class ViewAllService(HttpRpcHandler):
    """
    浏览服务列表
    """
    @require_login
    @web_adaptor(use_http_render=False)
    def get(self, *args, **kwargs):
        grp_services, grp_counts = ServiceMgr().web_pick()
        render_data = {'grp_service_dic': grp_services,
                       'grp_count_dic': grp_counts}
        self.render('service/view_all_service.html', **render_data)


@route(r'/view_logic_service', name='view_logic_service')
class ViewLogicService(HttpRpcHandler):
    """
    浏览逻辑服务
    """
    @require_login
    @web_adaptor(use_http_render=False)
    def get(self, *args, **kwargs):
        service = kwargs['service']
        grp_services, grp_counts = ServiceMgr().web_pick(service)
        render_data = {'grp_service_dic': grp_services,
                       'grp_count_dic': grp_counts,
                       "grp": service}
        self.render('service/view_service.html', **render_data)


@route(r'/save_service_data', name='save_service_data')
class SaveServiceData(HttpRpcHandler):
    """
    保存服务数据
    """
    @require_login
    @web_adaptor()
    @ajax_recv_wapper()
    def post(self, *args, **kwargs):
        try:
            new_grp_data_ls = ServiceMgr().web_unpick(kwargs['js_data'])
            grp = kwargs['grp']
            assert grp
        except:
            logger.warn("SaveServiceData::post error!!!, js_data:%s traceback:%s" % (kwargs['js_data'], traceback.format_exc()))
            return

        old_all_data_ls = ServiceMgr().get_init_data_ls()

        old_not_grp_data_ls = []
        old_grp_data_ls = []
        for service_dic in old_all_data_ls:
            if service_dic['service_group'] != grp:
                old_not_grp_data_ls.append(service_dic)
            else:
                old_grp_data_ls.append(service_dic)

        new_all_data_ls = new_grp_data_ls + old_not_grp_data_ls

        try:
            ServiceMgr().init(new_all_data_ls)
        except:
            logger.warn("SaveServiceData::post error!!!, data_ls:%s traceback:%s" % (new_grp_data_ls, traceback.format_exc()))
            ServiceMgr().init(old_all_data_ls)