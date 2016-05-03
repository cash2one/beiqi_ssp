# coding=utf-8
"""
Created on 2015-4-22

@author: Jay
"""
from utils.network.http import HttpRpcHandler
from utils.route import route
from utils.wapper.web import web_adaptor
from service_mgr.logic.web import setting as web_setting
from service_mgr.logic.web import require_login


@route(r'/common', name='common')
class Common(HttpRpcHandler):
    """
    通用
    """
    @require_login
    @web_adaptor(use_http_render=False)
    def get(self, *args, **kwargs):
        render_dict = {'func_list': web_setting.common_manager}
        self.render('main.html', **render_dict)