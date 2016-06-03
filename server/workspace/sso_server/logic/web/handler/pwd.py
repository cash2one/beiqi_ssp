#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/6

@author: Jay
"""
import time
import random
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.mysql_pack import pack as mysql_pack
from util.mq_packs.normal_sms_pack import pack as sms_notify_pack
from util.sso.account import *
from util.oem_conv import fix_account_postfix
from db.db_oper import DBBeiqiSspInst
from config import GMQDispRdsInts, GDevRdsInts, GAccRdsInts
from setting import DB_TBL_SSP_USR_LOGIN

SMS_SPEED_MAX = 20


@route(r'/pwd_new')
class NewPwdHandler(HttpRpcHandler):
    @web_adaptor()
    def post(self, account, val, pwd, *args, **kwargs):
        cur_account = fix_account_postfix(account)
        review_val = GAccRdsInts.send_multi_cmd(*combine_redis_cmds(review_lostpwd_val(cur_account)))
        if not review_val:
            return {'status': 3}

        if val != review_val:
            return {'status': 4}

        GAccRdsInts.send_multi_cmd(*combine_redis_cmds(
                pass_lostpwd_val(cur_account),
                set_account_pwd(cur_account, cipher_pwd(pwd), False)
            )
        )

        GMQDispRdsInts.send_cmd(*
            [shortcut_mq(
                'gen_mysql',
                mysql_pack(
                    DB_TBL_SSP_USR_LOGIN,
                    {
                        'username': cur_account,
                        'password': cipher_pwd(pwd),
                        'mobile': cur_account.split('@')[0],
                        # 'api_key': '840ebe7c2bfe4d529181063433ece0ef',
                    },
                    2
                )
            )]
        )
        return {'status': 0}


@route(r'/pwd_lost')
class LostPwdHandler(HttpRpcHandler):
    @web_adaptor()
    def post(self, account, api_key, *args, **kwargs):
        """
        密码丢失
        :param account:
        :param args:
        :param kwargs:
        :return:
        """
        cur_account = fix_account_postfix(account)
        if not GAccRdsInts.send_cmd(*exist_account(cur_account)):
            sql = 'select password from {0} where username=%s'.format(DB_TBL_SSP_USR_LOGIN)
            expect_pwd = DBBeiqiSspInst.query(sql, cur_account)
            if len(expect_pwd) == 0:
                return {'status': 1}

        mobile = get_mobile(GAccRdsInts, api_key, cur_account)
        if not mobile:
            return {'status': 2}

        sms_speed = GDevRdsInts.send_cmd(*get_sms_speed())
        if sms_speed is None:
            GDevRdsInts.send_multi_cmd(*combine_redis_cmds(init_sms_speed()))
        elif sms_speed >= SMS_SPEED_MAX:
            return {'status': 3}
        else:
            GDevRdsInts.send_cmd(*incr_sms_speed())

        ts = GDevRdsInts.send_cmd(*get_user_veri_sms_time(mobile))
        if ts is not None:
            logger.debug('veri sms, ts={0}'.format(ts))
            return {'status': 4}
        else:
            GDevRdsInts.send_multi_cmd(*combine_redis_cmds(set_user_veri_sms_time(mobile, time.time())))

        val = ''.join((str(random.randint(0, 9)) for _ in xrange(6)))
        logger.debug('lost pwd val: {0}'.format(val))
        GAccRdsInts.send_multi_cmd(*combine_redis_cmds(gen_lostpwd_val(cur_account, val)))
        GMQDispRdsInts.send_cmd(
            *shortcut_mq(
                'sms_notify',
                sms_notify_pack(mobile, 2, cur_account, mobile, val)
            )
        )
        return {'status': 0}