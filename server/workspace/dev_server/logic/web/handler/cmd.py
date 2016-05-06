#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/6

@author: Jay
"""
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.crypto.beiqi_sign import beiqi_tk_sign_wapper
from utils.wapper.web import web_adaptor
from util.redis_cmds.circles import *
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.cloud_push_pack import pack as push_pack
from dev_server.common import FEEDBACK_PATTERN, REPORT_KEYS, errno_map
from dev_server.config import GMQDispRdsInts, GDevRdsInts


@route(r'/cmd_report')
class CmdRptHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, user_name, sn, f, d, payload):
        logger.debug('cmd_rpt_v1 sn: {0}, d: {1}, f: {2}'.format(sn, d, f))
        primary = GDevRdsInts.execute([get_dev_primary(sn)])

        logger.debug('cmd rpt primary: {0}'.format(primary))
        if not primary:
            logger.debug('cmd rpt sn={0} no primary'.format(sn))
            self.send_error(400)
            return

        if f != primary:
            followers = GDevRdsInts.execute([get_dev_followers(sn)])
            if f not in followers:
                logger.debug('cmd rpt primary = {0}, f = {1}, sn = {2}, followers = {3]'.format(primary, f, sn, followers))
                self.send_error(400)
                return

        m = FEEDBACK_PATTERN.search(d)
        if not m:
            self.send_error(400)
            return

        user_cmd, cmd_ord, error_state = [m.groupdict().get(k) for k in REPORT_KEYS]

        if payload:
            description = payload
        else:
            description = errno_map.get(error_state) or 'fb_dft'

        logger.debug('cmd rpt desc: {0}'.format(description))

        GMQDispRdsInts.execute([shortcut_mq(
                'cloud_push',
                push_pack(
                    sn,
                    '{0}:{1}:{2}'.format(error_state, 'cmd_report', int(cmd_ord, 16)),
                    0,
                    description,
                    account=f
                )
            )]
        )
        return ''
