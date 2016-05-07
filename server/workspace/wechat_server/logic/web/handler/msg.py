#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/6

@author: Jay
"""
import time
import hashlib
from xml.etree import cElementTree as ElementTree
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from lib.msg_handler import msg_handlers, get_wechat_user, txt_return_template, fromUserName
from setting import TOKEN



@route(r'/wechat/')
class WeChatHandler(HttpRpcHandler):
    @web_adaptor(use_json_dumps=False)
    def get(self, signature, timestamp, nonce, echostr):
        args = [timestamp, nonce, TOKEN]
        args.sort()
        cal_sig = hashlib.sha1(''.join(args)).hexdigest()

        if cal_sig == signature:
            logger.debug('sig ok, echostr={0}'.format(echostr))
            return echostr
        else:
            logger.debug('cal_sig = {0}, signature={1}, echostr = {2}'.format(cal_sig, signature, echostr))
            self.send_error(400)
            return

    @web_adaptor(use_json_dumps=False)
    def post(self, signature='', timestamp='', nonce='', echostr=''):
        """
        :param signature:
        :param timestamp:
        :param nonce:
        :param echostr:
        :return:
        """
        if signature:
            args = [timestamp, nonce, TOKEN]
            args.sort()
            cal_sig = hashlib.sha1(''.join(args)).hexdigest()

            if cal_sig != signature:
                logger.debug('cal_sig = {0}, signature={1}, echostr = {2}'.format(cal_sig, signature, echostr))
                self.send_error(400)
                return

        body = self.request.body
        logger.debug('body = %r', body)
        if not body:
            return ''

        e = ElementTree.fromstring(body)
        msg_type = e.find('MsgType').text
        username = get_wechat_user(e)
        h = msg_handlers.get(msg_type)
        if not h:
            logger.debug('WeChatHandler msg_type:%s not has handler!!!', msg_type)
            logger.debug('msgType = %r', msg_type)
            content = '仅限发送图片、小视频和语音到亲友圈'
            reply = txt_return_template.format(username[3:], fromUserName, str(int(time.time())), 'text', content)
            self.finish(reply)
            return

        h(self, e)
        return
