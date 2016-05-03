# coding=utf-8
"""
Created on 2015-4-22

@author: Jay
"""
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from utils.web import cookie
from utils.web.verify_code import render_verify_code
from service_mgr.logic.web import setting as web_setting
from service_mgr.logic.web import require_login

@route(r'/', name='login_html')  # 首页
class LoginHandle(HttpRpcHandler):
    @web_adaptor(use_http_render=False)
    def get(self):
        self.render('login.html')
    
    @web_adaptor(use_http_render=False)
    def post(self, username, password, verify_code):
        if not cookie.check_cookie(self, "service_mgr_verify_code", verify_code):
            self.reponse_msg("验证码错误!!!")
            return
        user = "test"
        if user:
            seesionid = self.get_secure_cookie('sid')
            self._sessions_[seesionid] = user
            self.redirect('/index')
        else:
            self.write('登录失败')
            self.finish()


@route(r'/index', name='index')   # 首页
class IndexHandle(HttpRpcHandler):
    @require_login
    @web_adaptor(use_http_render=False)
    def get(self, *args, **kwargs):
        user = "server"
        render_dict = {'user_name': user, 'sub_frames': web_setting.menu}
        self.render('index.html', **render_dict)

@route(r'/verify_code', name='verify_code')   # 验证码
class VerifyCodeHandle(HttpRpcHandler):
    @web_adaptor(use_http_render=False)
    def get(self, *args, **kwargs):
        render_verify_code(self, cookie_name="service_mgr_verify_code")

@route(r'/logout', name='logout')  # 登出
class LoginHandle(HttpRpcHandler):
    @web_adaptor(use_http_render=False)
    def get(self):
        self.redirect('/')

