#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/6

@author: Jay
"""
import urllib
import time
from datetime import datetime
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.mysql_pack import pack as mysql_pack
from util.convert import is_mobile, is_reg_val_code
from config import GMQDispRdsInts, GDevRdsInts, GAccRdsInts
from util.sso.account import get_newacc_reg_val, set_account_pwd, cipher_pwd
from util.convert import bs2utf8, is_email, combine_redis_cmds
from util.sso.account import get_sms_speed, incr_sms_speed, init_sms_speed, get_user_veri_sms_time, set_user_veri_sms_time
from common.reg import reg_via_mobile
from setting import DB_TBL_SSP_USR_LOGIN


SMS_SPEED_MAX = 20

user_info_tbl = 'user_info'
fmt = '%Y-%m-%d %H:%M:%S'


@route(r'/check_reg_val_code')
class CheckRegValCodeHandler(HttpRpcHandler):
    @web_adaptor()
    def post(self, user_name ,pwd):
        """
        检查注册验证码
        """
        user_agent = urllib.unquote(bs2utf8(self.request.headers['user-agent']))

        reg_ip = bs2utf8(self.request.remote_ip)
        if not is_email(user_name):
            return {'status': 1}

        mobile = user_name.partition('@')[0]
        if not is_mobile(mobile):
            return {'status': 2}

        val = bs2utf8(self.get_argument('val'))
        if not is_reg_val_code(val):
            return {'status': 3}

        expect_code = GAccRdsInts.send_cmd(*get_newacc_reg_val(mobile))
        if not expect_code:
            return {'status': 4}
        expect_code = expect_code.split(':')[0]
        if expect_code != val:
            return {'status': 4}

        pwd_mask = cipher_pwd(pwd)
        ok = GAccRdsInts.send_cmd(*set_account_pwd(user_name, pwd_mask))
        if not ok:
            return {'status': 5}

        reg_ts = time.strftime(fmt, time.gmtime())
        GMQDispRdsInts.send_multi_cmd(*combine_redis_cmds(
            shortcut_mq(
                'gen_mysql',
                mysql_pack(
                    DB_TBL_SSP_USR_LOGIN,
                    {
                        'username': user_name,
                        'password': pwd_mask,
                        'mobile': mobile,
                    },
                    0
                )
            ),
            shortcut_mq(
                'gen_mysql',
                mysql_pack(
                    DB_TBL_SSP_USR_LOGIN,
                    {
                        'username': user_name,
                        'reg_agent': user_agent,
                        'reg_ts': reg_ts,
                        'reg_ip': reg_ip,
                    },
                    action=0,
                )
            )
        ))
        return {'status': 0}


@route(r'/req_reg_val_code')
class GenRegCodeHandler(HttpRpcHandler):
    @web_adaptor()
    def post(self):
        """
    请求发送注册验证短信
        """
        account = bs2utf8(self.get_argument('account'))
        if not is_email(account):
            logger.warn('account:%s illegal' % account)
            return {'status': 1}

        mobile = account.split('@')[0]

        sms_speed = GDevRdsInts.send_cmd(*get_sms_speed())
        if sms_speed is None:
            GDevRdsInts.send_multi_cmd(*combine_redis_cmds(*combine_redis_cmds(init_sms_speed())))
        elif sms_speed >= SMS_SPEED_MAX:
            logger.debug('sms speed max, mobile={0}, {1}'.format(mobile, datetime.now().isoformat()))
            return {'status': 3}
        else:
            GDevRdsInts.send_cmd(*incr_sms_speed())

        ts = GDevRdsInts.send_cmd(*get_user_veri_sms_time(mobile))
        if ts is not None:
            logger.debug('veri sms, ts={0}'.format(ts))
            return {'status': 4}
        else:
            GDevRdsInts.send_multi_cmd(*combine_redis_cmds(set_user_veri_sms_time(mobile, time.time())))

        if not reg_via_mobile(account, None):
            return {'status': 2}
        return {'status': 0}
