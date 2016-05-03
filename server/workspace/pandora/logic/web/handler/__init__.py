#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-17

@author: Jay
"""
import os
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor


@route(r'/get_public_key', name='get_public_key')
class GetPublicKeyHandle(HttpRpcHandler):
    """
    获取公有密钥处理器
    """
    @web_adaptor(use_json_dumps=False)
    def get(self):
        """
        http get 请求
        :return:
        """
        public_key_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
                                       "common_server",
                                       "utils",
                                       "CA",
                                       "server_public.key")
        return open(public_key_path).read()

