#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/2

@author: Jay
"""
import urllib2
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.cloud_push_pack import pack as push_pack
from util.convert import bs2utf8
from config import GMQDispRdsInts
from utils.crypto.beiqi_sign import beiqi_tk_sign_wapper


@route(r'/chat/bcast')
class ChatBCastHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, user_name, file_type, fn, ref, thumb_fn, thumb_ref, text):
        des = bs2utf8(':'.join([urllib2.quote(bs2utf8(v)) for v in (user_name,  file_type, fn, ref, thumb_fn, thumb_ref,text)]))

        GMQDispRdsInts.send_cmd(*
            shortcut_mq('chat_msg',
                        push_pack(user_name, 'msg', 2, '', des)
                        )
        )