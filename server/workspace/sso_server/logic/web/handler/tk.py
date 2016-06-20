#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/6

@author: Jay
"""
import time
import urllib
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.mysql_pack import pack as mysql_pack
from util.convert import is_email, bs2utf8
from util.sso.account import get_pwd, cipher_pwd
from util.oem_account_key import beiqi_keys
from util.redis_cmds.circles import get_tk_time, set_tk_time, get_sn_of_gid
from util.sso_common.build_sso_token import gen_token, decrypt_username
from db.db_oper import DBBeiqiSspInst
from config import GMQDispRdsInts, GDevRdsInts, GAccRdsInts
from setting import DB_TBL_DEVICE_INFO, DB_TBL_USER_INFO

fmt = '%Y-%m-%d %H:%M:%S'


@route(r'/gen_tk')
class BeiqiSSOHandler(HttpRpcHandler):
    @web_adaptor(use_json_dumps=False)
    def get(self, username, api_key, pwd="", *args, **kwargs):
        """
        生成SSO认证token
        :param username:
        :param api_key:
        :param pwd: device no pwd, app account has pwd
        :param args:
        :param kwargs:
        :return:
        """

        user_agent = urllib.unquote(bs2utf8(self.request.headers['user-agent']))
        api_ob = beiqi_keys.get(api_key)
        if not api_ob:
            logger.warn("gen_tk api_ob:%s, api_key:%s" % (api_ob, api_key))
            self.set_status(401)
            return

        remote_ip = bs2utf8(self.request.remote_ip)

        if not is_email(username):
            # 设备没有pid时登录
            rc4_key = api_ob.get('rc4_key')
            if rc4_key is None:
                logger.debug('api_key={0}, username={1} rc4_key not exists'.format(api_key, username))
                self.set_status(400)
                return

            sn, ts = decrypt_username(username, rc4_key)
            sql = "SELECT 1 FROM {db} WHERE sn = '{sn}'".format(db=DB_TBL_DEVICE_INFO, sn=sn)
            ret_list = DBBeiqiSspInst.query(sql)
            if len(ret_list) == 0:
                logger.debug('ret_list={0}, sn={1}'.format(ret_list, sn))
                self.set_status(400)
                return

            saved_ts = GDevRdsInts.send_cmd(*get_tk_time(sn))
            if saved_ts == ts:
                logger.debug('ts={0} the same with saved_ts'.format(ts))
                self.set_status(400)
                return

            GDevRdsInts.send_cmd(*set_tk_time(sn, ts))

            login_ts = time.strftime(fmt, time.gmtime())
            GMQDispRdsInts.send_cmd(
                *shortcut_mq('gen_mysql',
                    mysql_pack(DB_TBL_USER_INFO,
                               {'last_login_ts': login_ts, 'last_login_ip': remote_ip, 'last_login_agent': user_agent},
                               action=2,
                               ref_kvs={'username': sn}
                               )
                )
            )
            return gen_token(api_ob.get('s'), sn, 1, account_rds=GAccRdsInts)

        gid = username.split('@')[0]
        if len(gid) == 6:
            # 设备登录
            sn = GDevRdsInts.send_cmd(*get_sn_of_gid(gid))
            logger.debug('beiqi sso, username=%r, gid=%r, sn=%r' % (username, gid, sn))
            # primary = dev_filter.send_cmd(*get_dev_primary(pid))
            if sn:
                # django used gmttime, so we'd better use gmttime.
                login_ts = time.strftime(fmt, time.gmtime())
                GMQDispRdsInts.send_cmd(
                    *shortcut_mq('gen_mysql',
                        mysql_pack(DB_TBL_USER_INFO,
                                   {'last_login_ts': login_ts, 'last_login_ip': remote_ip, 'last_login_agent': user_agent},
                                   action=2,
                                   ref_kvs={'username': username}
                                   )
                    )
                )
                return gen_token(api_ob.get('s'), username, 1, account_rds=GAccRdsInts)
            else:
                logger.debug('gid={0} invalid no sn'.format(gid))
                self.set_status(403)
                return

        expect_pwd = GAccRdsInts.send_cmd(*get_pwd(username))

        if expect_pwd is not None:
            if expect_pwd != cipher_pwd(pwd):
                logger.warn('pwd incorrect: username = {0}, pwd={1}, expect_pwd={2}'.format(username, cipher_pwd(pwd), expect_pwd))
                self.set_status(401)
                return
        else:
            # not in redis, check mysql
            sql = "select password from {db} where username='{username}'".format(db='ssp_user_login', username=username)
            expect_pwd = DBBeiqiSspInst.query(sql)
            if len(expect_pwd) == 0:
                logger.debug('account={0} not exist'.format(username))
                self.set_status(401)
                return
            else:
                pwd_inmysql = expect_pwd[0].get('password')
                pwd_inmysql = pwd_inmysql.encode('utf8') if pwd_inmysql is not None else pwd_inmysql
                if pwd_inmysql != cipher_pwd(pwd):
                    logger.debug('pwd incorrect: username = {0}, pwd={1}, expect_pwd={2}'.format(username, cipher_pwd(pwd), expect_pwd))
                    self.set_status(401)
                    return

        login_ts = time.strftime(fmt, time.gmtime())
        GMQDispRdsInts.send_cmd(
            *shortcut_mq('gen_mysql',
                mysql_pack(DB_TBL_USER_INFO,
                           {'last_login_ts': login_ts, 'last_login_ip': remote_ip, 'last_login_agent': user_agent},
                           action=2,
                           ref_kvs={'username': username}
                           )
            )
        )
        return gen_token(api_ob.get('s'), username, 1, account_rds=GAccRdsInts)
