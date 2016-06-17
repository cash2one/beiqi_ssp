#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/6

@author: Jay
"""
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from util.sso.account import set_account_pwd
from util.convert import bs2utf8, is_email
from util.sso.account import exist_account
from db.db_oper import DBBeiqiSspInst
from config import GAccRdsInts
from setting import DB_TBL_SSP_USR_LOGIN



SMS_SPEED_MAX = 20
fmt = '%Y-%m-%d %H:%M:%S'


@route(r'/valid_acc_new')
class AccountStateHandler(HttpRpcHandler):
    @web_adaptor()
    def post(self, account, *args, **kwargs):
        """
    帐号状态，是否已存在
        """
        if not is_email(account):
            return {'status': 1}

        #帐号存在并已激活
        account_exist = GAccRdsInts.send_cmd(*exist_account(account))
        if account_exist:
            return {'status': 2}

        sql = "select * from {db} where username='{user_name}'".format(db=DB_TBL_SSP_USR_LOGIN, user_name=account)
        res = DBBeiqiSspInst.query(sql)
        if len(res) != 0:
            # exist in mysql, so we cache it
            pwd = res[0].get('password').encode('utf8')
            GAccRdsInts.send_cmd(*set_account_pwd(account, pwd))
            return {'status': 2}

        return {'status': 0}
