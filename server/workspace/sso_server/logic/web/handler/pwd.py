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
from utils.crypto.beiqi_sign import beiqi_tk_sign_wapper
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.mysql_pack import pack as mysql_pack
from util.mq_packs.normal_sms_pack import pack as sms_notify_pack
from util.convert import bs2utf8
from util.sso.account import *
from util.oem_conv import fix_account_postfix
from db.db_oper import DBBeiqiSspInst
from config import GMQDispRdsInts, GDevRdsInts, GAccRdsInts

SMS_SPEED_MAX = 20


@route(r'/pwd_new')
class NewPwdHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def post(self, account, val, pwd, *args, **kwargs):
        cur_account = fix_account_postfix(account)
        review_val = GAccRdsInts.pipe_execute((review_lostpwd_val(cur_account)))
        if not review_val:
            return {'status': 3}

        if val != review_val:
            return {'status': 4}

        GAccRdsInts.pipe_execute((
                pass_lostpwd_val(cur_account),
                set_account_pwd(cur_account, cipher_pwd(pwd), False)
            )
        )

        GMQDispRdsInts.execute(
            [shortcut_mq(
                'gen_mysql',
                mysql_pack(
                    'ssp_user_login',
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
    @beiqi_tk_sign_wapper()
    def post(self, account, *args, **kwargs):
        """
        密码丢失
        :param account:
        :param args:
        :param kwargs:
        :return:
        """
        cur_account = fix_account_postfix(account)
        if not GAccRdsInts.execute(exist_account(cur_account)):
            sql = 'select password from {0} where username=%s'.format('ssp_user_login')
            expect_pwd = DBBeiqiSspInst.query(sql, cur_account)
            if len(expect_pwd) == 0:
                return {'status': 1}

        api_key = bs2utf8(self.get_argument('api_key', None))
        mobile = get_mobile(GAccRdsInts, api_key, cur_account)
        if not mobile:
            return {'status': 2}

        sms_speed = GDevRdsInts.execute(get_sms_speed())
        if sms_speed is None:
            GDevRdsInts.pipe_execute(init_sms_speed())
        elif sms_speed >= SMS_SPEED_MAX:
            return {'status': 3}
        else:
            GDevRdsInts.execute(incr_sms_speed())

        ts = GDevRdsInts.execute(get_user_veri_sms_time(mobile))
        if ts is not None:
            logger.debug('veri sms, ts={0}'.format(ts))
            return {'status': 4}
        else:
            GDevRdsInts.pipe_execute(set_user_veri_sms_time(mobile, time.time()))

        val = ''.join((str(random.randint(0, 9)) for _ in xrange(6)))
        logger.debug('lost pwd val: {0}'.format(val))
        GAccRdsInts.pipe_execute(gen_lostpwd_val(cur_account, val))
        GMQDispRdsInts.execute(
            shortcut_mq(
                'sms_notify',
                sms_notify_pack(mobile, 2, cur_account, mobile, val)
            )
        )
        return {'status': 0}