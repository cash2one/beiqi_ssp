#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/4

@author: Jay
"""
import ujson
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from api_server.config import GAccRdsInts, GCalcRdsInts, GDevRdsInts, GMQDispRdsInts
from util.sso.account import get_mobile
from util.redis_cmds.user_info import *
from util.redis_cmds.circles import *
from util.convert import bs2utf8
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.mysql_pack import pack as mysql_pack
from util.redis_cmds.mqtt import get_mqtt_status

user_tbl = 'user_info'


@route(r'/account/token')
class AccountTokenHandle(HttpRpcHandler):
    """
    账号token
    """
    @web_adaptor()
    def get(self, Username):
        """
        绑定用户和设备的关系
        """
        return {'token': Username,
                'mobile': get_mobile(GAccRdsInts, self.request.headers.get('A-PreKey'), Username)}


@route(r'/account/bind_push')
class AccountBindPushHandler(HttpRpcHandler):
    @web_adaptor()
    def get(self, account, os, ver, args):
        logger.debug('bind push platform: {0}, ver: {1}, args: {2}, cur_account: {3}'.format(os, ver, args, account))

        ensure_func = globals().get('_'.join((os, 'ok')))
        logger.debug('bind push ensure_func: {0}'.format(ensure_func))
        if not ensure_func:
            logger.debug('bind push ensure_func: {0}'.format(ensure_func))
            self.send_error(400)
            return

        args = ensure_func(args)
        logger.debug('bind push args: {0}'.format(args))
        if not args:
            logger.debug('bind push args: {0}'.format(args))
            self.send_error(400)
            return

        _ = [os, ver]
        _.extend(args)

        GAccRdsInts.execute(['set', 'account:{0}'.format(account), ':'.join(_)])


@route(r'/account/unbind_push')
class AccountUnbindPushHandler(HttpRpcHandler):
    @web_adaptor()
    def get(self, account):
        GCalcRdsInts.execute(['delete', 'account:{0}'.format(account)])


@route(r'/get_user_info')
class GetUserInfoHandler(HttpRpcHandler):
    @web_adaptor()
    def get(self, user):
        payload = GDevRdsInts.send_cmd(*get_user_info(user))
        if payload is None:
            return {'status': 1}
        return payload


@route(r'/set_user_info')
class GetUserInfoHandler(HttpRpcHandler):
    @web_adaptor()
    def post(self, Username, payload, sn='', gid=''):
        logger.debug('username=%r, sn=%r, gid=%r, payload=%r' % (Username, sn, gid, payload))
        nickname = bs2utf8(ujson.loads(payload).get('nickname'))

        if gid != '':
            primary = GDevRdsInts.execute([get_group_primary(gid)])
            if Username != primary:
                return {'status': 2}

            GDevRdsInts.execute([set_user_info(gid, payload)])
            GDevRdsInts.execute([set_user_nickname(gid, nickname)])
            return {'status': 0}

        if sn != '':
            primary = GDevRdsInts.execute([get_dev_primary(sn)])
            if Username != primary:
                return {'status': 3}

            GDevRdsInts.execute([set_user_info(sn, payload)])
            GDevRdsInts.execute([set_user_nickname(sn, nickname)])
            return {'status': 0}

        GDevRdsInts.execute([set_user_info(Username, payload)])
        GDevRdsInts.execute([set_user_nickname(Username, nickname)])

        GMQDispRdsInts.send_cmd(
            *shortcut_mq('gen_mysql',
                mysql_pack(user_tbl,
                           {'nickname': nickname},
                            action=2,
                            ref_kvs={'username': Username}
                )
            )
        )

        return {'status': 0}


@route(r'/get_msglist')
class GetMsglistHandler(HttpRpcHandler):
    @web_adaptor()
    def post(self, Username):
        sns = GDevRdsInts.execute([get_user_devs(Username)])
        if sns is None:
            return {'status': 1}

        msg_list = {}
        for sn in sns:
            gid = GDevRdsInts.execute([get_gid_of_sn(sn)])
            if gid:
                msgs = GDevRdsInts.execute([get_user_group_msglist(Username, gid)])
                msg_list[gid] = msgs

        system_msg = GDevRdsInts.execute([get_user_system_msglist(Username)])

        msg_list['system'] = system_msg

        logger.debug('user=%r, msg_list=%r' % (Username, msg_list))
        return msg_list


@route(r'/get_status')
class GetStatusHandler(HttpRpcHandler):
    @web_adaptor()
    def get(self, Username, user_list):
        user_list = ujson.loads(user_list)

        ret = {}
        for user in user_list:
            user = bs2utf8(user)
            status = GDevRdsInts.execute([get_mqtt_status(user)])
            ret[user] = status
        return ret