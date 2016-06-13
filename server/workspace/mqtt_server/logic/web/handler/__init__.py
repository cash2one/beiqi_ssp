#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-17

@author: Jay
"""
import ujson
from util.convert import bs2utf8
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from utils.crypto.beiqi_sign import beiqi_tk_sign_wapper
from util.redis_cmds.mqtt import get_mqtt_status
from mqtt_server.config import GDevRdsInts


@route(r'/get_status')
class GetStatusHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, user_name, user_list):
        user_list = ujson.loads(user_list)

        ret = {}
        for user in user_list:
            user = bs2utf8(user)
            status = GDevRdsInts.send_cmd(*get_mqtt_status(user))
            ret[user] = status
        return ret
