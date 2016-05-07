#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/6

@author: Jay
"""
import ujson
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from utils.network.http import HttpRpcClient
from util.redis_cmds.circles import getall_wechat_devs
from util.redis_cmds.wechat import get_wechat_access_token, get_wechat_ticket
from lib.add_device import add_device
from lib.sign import Sign
from config import GDevRdsInts, GAccRdsInts
from setting import WECHAT_SERACH_DEVICE, APPID, APPSECRET


dev_info_tbl = 'device_info'
user_info_tbl = 'user_info'


@route(r'/wechat/pages/add_device')
class AddDeviceHandler(HttpRpcHandler):
    @web_adaptor(use_http_render=False)
    def get(self):
        code = self.get_argument('code')
        if code:
            grant_type = 'authorization_code'
            args = '?appid={0}&secret={1}&code={2}&grant_type={3}'.format(APPID, APPSECRET, code, grant_type)
            url = 'https://api.weixin.qq.com/sns/oauth2/access_token' + args
            resp = HttpRpcClient().fetch_async(url=url)
            resp = resp.body
            logger.debug('resp = %r', resp)
            resp = ujson.loads(resp)
            #get wechat user info
            token = resp.get('access_token')
            openid = resp.get('openid')
            userinfo_args = '?access_token={0}&openid={1}&lang=zh_CN'.format(token, openid)
            userinfo_url = 'https://api.weixin.qq.com/sns/userinfo' + userinfo_args
            user_resp = HttpRpcClient().fetch_async(url=userinfo_url)
            str_user_resp = user_resp.body
            logger.debug('user_resp = %r', str_user_resp)
            user_resp = ujson.loads(str_user_resp)
            self.render('wechat_add_device.html', payload=user_resp)
            return
        else:
            self.send_error(400)
            return

    @web_adaptor()
    def post(self, username, code, payload):
        logger.debug(u'add_device post, username={0}, user_info={1}, code={2}'.format(username, payload, code))
        user_info = ujson.loads(payload)
        if code == '' or username == '' or user_info == '':
            self.send_error(400)
            return

        if len(code) == 9:
            self.send_error(400)
            return

        if len(code) == 6:
            # gid, 关注
            status = add_device(username, code, user_info)
            return status
        else:
            return {'status': 1}


@route(r'/wechat/pages/manage_dev')
class ManageDevHandler(HttpRpcHandler):
    @web_adaptor(use_http_render=False)
    def get(self, code):
        grant_type = 'authorization_code'
        args = '?appid={0}&secret={1}&code={2}&grant_type={3}'.format(APPID, APPSECRET, code, grant_type)
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token' + args
        resp = HttpRpcClient().fetch_async(url=url)
        resp = resp.body
        logger.debug('resp = %r', resp)
        resp = ujson.loads(resp)
        #get wechat user info
        token = resp.get('access_token')
        openid = resp.get('openid')
        if openid:
            username = 'wx#' + openid
            dev_set = GDevRdsInts.send_cmd(*getall_wechat_devs(username))
            dev_list = []
            for dev in dev_set.iteritems():
                dev_obj = {}
                dev_obj['gid'] = dev[0]
                dev_obj['nickname'] = dev[1]
                dev_list.append(dev_obj)
            logger.debug('dev_list = %r, username = %r', dev_list, username)
            self.render('wechat_manage_dev.html', dev_list=dev_list, username=username)
        return


@route(r'/wechat/pages/search_device')
class SearchDeviceHandler(HttpRpcHandler):
    @web_adaptor(use_http_render=False)
    def get(self):
        access_token = GAccRdsInts.send_cmd(*get_wechat_access_token())
        ticket = GAccRdsInts.send_cmd(*get_wechat_ticket())
        sign_data = Sign(ticket, WECHAT_SERACH_DEVICE).sign()
        logger.debug('access_token:%s ticket:%s sign_data:%s'%(access_token, ticket, sign_data))
        self.render('wechat_search_dev.html',
                    appid=APPID,
                    timestamp=sign_data.get('timestamp'),
                    nonceStr=sign_data.get('nonceStr'),
                    signature=sign_data.get('signature'))
        return