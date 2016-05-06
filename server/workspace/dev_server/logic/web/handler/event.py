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
from util.convert import bs2unicode
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.cloud_push_pack import pack as push_pack
from util.redis_cmds.user_info import get_geo_fence
from dev_server.config import GMQDispRdsInts, GDevRdsInts


@route(r'/event_report')
class EventReportHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def post(self, user_name, sn, payload):
        logger.debug(u'event report -- acc={0}, sn={1}, payload={2}'.format(user_name, sn, bs2unicode(payload)))
        payload = ujson.loads(payload)
        reason = payload.get('reason')
        if reason == 'geo_fence_alert':
            attr = payload.get('attr')
            ts = payload.get('ts')
            longitude = attr.get('lon')
            latitude = attr.get('lat')
            radius = attr.get('rad')

            _ = GDevRdsInts.execute([get_geo_fence(user_name, longitude, latitude, radius)])
            creator, name = _.split(':')

            GMQDispRdsInts.pipe_execute(
                [shortcut_mq(
                    'cloud_push',
                    push_pack(user_name, 'geo_fence_alertqqq', 2, payload, account=creator)
                )]
            )
        sample_freq = 600
        next_latency = 3600
        return {'state': 0, 'next_latency': next_latency, 'sample_freq': sample_freq}
