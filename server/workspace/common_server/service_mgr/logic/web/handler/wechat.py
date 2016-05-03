#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-8-18

@author: Jay
"""
import traceback
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor, ajax_recv_wapper
from service_mgr.lib.wechat import WechatMgr
from service_mgr.logic.web import require_login
from service_mgr.db.db_oper import DBWechatInst
from service_mgr.lib.lib_wechat.menu import MenuManager


@route(r'/view_wechat', name='view_wechat')
class ViewWechat(HttpRpcHandler):
    """
    全局微信配置
    """
    @require_login
    @web_adaptor(use_http_render=False)
    def get(self, *args, **kwargs):
        render_data = {'pick_ls': WechatMgr().web_pick()}
        self.render('common/wechat.html', **render_data)


@route(r'/save_wechat_data', name='save_wechat_data')
class SaveWechatData(HttpRpcHandler):
    """
    保存微信数据
    """
    @require_login
    @web_adaptor()
    @ajax_recv_wapper()
    def post(self, *args, **kwargs):
        try:
            data_ls = WechatMgr().web_unpick(kwargs['js_data'])
        except:
            logger.warn("SaveWechatData::post error!!!, js_data:%s traceback:%s" % (kwargs['js_data'], traceback.format_exc()))
            return

        last_data_ls = WechatMgr().get_init_data_ls()

        try:
            DBWechatInst.update_diff(last_data_ls, data_ls)
            WechatMgr().init(data_ls)
        except:
            logger.warn("SaveWechatData::post error!!!, data_ls:%s traceback:%s" % (data_ls, traceback.format_exc()))
            WechatMgr().init(last_data_ls)


@route(r'/publish_wechat_menu', name='publish_wechat_menu')
class PublishWechatMenu(HttpRpcHandler):
    """
    发布微信菜单
    """
    @require_login
    @web_adaptor()
    @ajax_recv_wapper()
    def post(self, *args, **kwargs):
        MenuManager().create_menu(WechatMgr().gen_menu_str())