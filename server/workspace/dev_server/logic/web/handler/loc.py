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
from utils.crypto.beiqi_sign import beiqi_tk_sign_wapper
from util.convert import bs2utf8, combine_redis_cmds
from config import GMQDispRdsInts
from common.mq import build_mq_package


@route(r'/loc_v1')
class LocationV1Handler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def post(self, user_name, sn, payload, dev_type=''):
        logger.debug(u'loc v1 -- acc={0}, sn={1}, payload={2}'.format(user_name, sn, payload))

        payload = ujson.loads(payload)
        for k, v in payload.iteritems():
            k = bs2utf8(k)
            v = bs2utf8(v)

        GMQDispRdsInts.send_multi_cmd(*combine_redis_cmds(*build_mq_package(user_name, sn, dev_type, payload)))

        sample_freq = 600
        next_latency = 3600
        return {'state': 0, 'next_latency': next_latency, 'sample_freq': sample_freq}