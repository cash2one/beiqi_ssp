#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-27

@author: Jay
"""
import traceback
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor, ajax_recv_wapper
from service_mgr.lib.tp_service import TPServiceMgr
from service_mgr.db.db_oper import DBTpServiceInst
from service_mgr.logic.web import require_login


@route(r'/view_tp_service', name='view_tp_service')
class ViewTPService(HttpRpcHandler):
    """
    查看第三方服务
    """
    @require_login
    @web_adaptor(use_http_render=False)
    def get(self, *args, **kwargs):
        render_data = {'tp_service_data': TPServiceMgr().web_pick()}
        self.render('common/tp_service.html', **render_data)


@route(r'/save_tp_service_data', name='save_tp_service_data')
class SaveTPServiceData(HttpRpcHandler):
    """
    保存第三方服务数据
    """
    @require_login
    @web_adaptor()
    @ajax_recv_wapper()
    def post(self, *args, **kwargs):
        try:
            data_ls = TPServiceMgr().web_unpick(kwargs['js_data'])
        except:
            logger.warn("SaveTPServiceData::post error!!!, js_data:%s traceback:%s" % (kwargs['js_data'], traceback.format_exc()))
            return

        last_data_ls = TPServiceMgr().get_init_data_ls()

        try:
            DBTpServiceInst.update_diff(TPServiceMgr().db_pick(last_data_ls), TPServiceMgr().db_pick(data_ls))
            TPServiceMgr().init(data_ls)
        except:
            logger.warn("SaveTPServiceData::post error!!!, data_ls:%s traceback:%s" % (data_ls, traceback.format_exc()))
            TPServiceMgr().init(last_data_ls)
