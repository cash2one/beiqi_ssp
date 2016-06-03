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
from util.sso.account import get_mobile
from util.redis_cmds.user_info import *
from util.redis_cmds.circles import *
from util.convert import bs2utf8
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.mysql_pack import pack as mysql_pack
from util.redis_cmds.mqtt import get_mqtt_status
from utils.crypto.beiqi_sign import beiqi_tk_sign_wapper
from config import GAccRdsInts, GCalcRdsInts, GDevRdsInts, GMQDispRdsInts
from setting import DB_TBL_USER_INFO


@route(r'/account/token')
class AccountTokenHandle(HttpRpcHandler):
    """
    账号token
    """
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, user_name):
        """
        绑定用户和设备的关系
        """
        return {'token': user_name,
                'mobile': get_mobile(GAccRdsInts, self.request.headers.get('A-PreKey'), user_name)}


@route(r'/account/bind_push')
class AccountBindPushHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
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

        GAccRdsInts.send_cmd('set', 'account:{0}'.format(account), ':'.join(_))


@route(r'/account/unbind_push')
class AccountUnbindPushHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, account):
        GCalcRdsInts.send_cmd('delete', 'account:{0}'.format(account))


@route(r'/get_user_info')
class GetUserInfoHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, user):
        payload = GDevRdsInts.send_cmd(*get_user_info(user))
        if payload is None:
            return {'status': 1}
        return payload


@route(r'/set_user_info')
class GetUserInfoHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def post(self, user_name, payload, sn='', gid=''):
        logger.debug('user_name=%r, sn=%r, gid=%r, payload=%r' % (user_name, sn, gid, payload))
        nickname = bs2utf8(ujson.loads(payload).get('nickname'))

        if gid != '':
            primary = GDevRdsInts.send_cmd(*get_group_primary(gid))
            if user_name != primary:
                return {'status': 2}

            GDevRdsInts.send_cmd(*set_user_info(gid, payload))
            GDevRdsInts.send_cmd(*set_user_nickname(gid, nickname))
            return {'status': 0}

        if sn != '':
            primary = GDevRdsInts.send_cmd(*get_dev_primary(sn))
            if user_name != primary:
                return {'status': 3}

            GDevRdsInts.send_cmd(*set_user_info(sn, payload))
            GDevRdsInts.send_cmd(*set_user_nickname(sn, nickname))
            return {'status': 0}

        GDevRdsInts.send_cmd(*set_user_info(user_name, payload))
        GDevRdsInts.send_cmd(*set_user_nickname(user_name, nickname))

        GMQDispRdsInts.send_cmd(
            *shortcut_mq('gen_mysql',
                mysql_pack(DB_TBL_USER_INFO,
                           {'nickname': nickname},
                           action=2,
                           ref_kvs={'user_name': user_name}
                           )
            )
        )

        return {'status': 0}


@route(r'/get_msglist')
class GetMsglistHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def post(self, user_name):
        sns = GDevRdsInts.send_cmd(*get_user_devs(user_name))
        if sns is None:
            return {'status': 1}

        msg_list = {}
        for sn in sns:
            gid = GDevRdsInts.send_cmd(*get_gid_of_sn(sn))
            if gid:
                msgs = GDevRdsInts.send_cmd(*get_user_group_msglist(user_name, gid))
                msg_list[gid] = msgs

        system_msg = GDevRdsInts.send_cmd(*get_user_system_msglist(user_name))

        msg_list['system'] = system_msg

        logger.debug('user=%r, msg_list=%r' % (user_name, msg_list))
        return msg_list


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