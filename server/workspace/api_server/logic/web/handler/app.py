#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/4

@author: Jay
"""
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.cloud_push_pack import pack as push_pack
from util.redis_cmds.cloud_app import *
from config import GDevRdsInts, GMQDispRdsInts, GAccRdsInts
from util.redis_cmds.user_info import *
from utils.crypto.beiqi_sign import client_sign_wapper


@route(r'/app/set_app_data')
class SetAppDataHandler(HttpRpcHandler):
    @web_adaptor()
    @client_sign_wapper(GAccRdsInts)
    def get(self, user_name, receiver, app, payload, *args, **kwargs):
        now = str(time.time())
        payload = '$'.join((user_name, payload))
        result = GDevRdsInts.send_cmd(*set_app_data(receiver, app, now, payload))
        logger.debug(u'result = %r', result)

        GMQDispRdsInts.send_cmd(*
            shortcut_mq('cloud_push',
                        push_pack(user_name, 'set_app_data', 2, payload, account=receiver))
        )
        return {'status': 0}


@route(r'/app/get_app_data')
class GetAppDataHandler(HttpRpcHandler):
    @web_adaptor()
    @client_sign_wapper(GAccRdsInts)
    def get(self, user_name, receiver, app, ts='', *args, **kwargs):
        if ts:
            data = GDevRdsInts.send_cmd(*get_app_data_by_ts(receiver, app, ts))
        else:
            data = GDevRdsInts.send_cmd(*get_app_data(receiver, app))
        logger.debug(u'data = %r', data)
        return data


@route(r'/app/del_app_data')
class DelAppDataHandler(HttpRpcHandler):
    @web_adaptor()
    @client_sign_wapper(GAccRdsInts)
    def get(self, user_name, receiver, app, ts, *args, **kwargs):
        result = GDevRdsInts.send_cmd(*del_app_data(receiver, app, ts))
        logger.debug(u'result = %r', result)
        return {'status': 0}