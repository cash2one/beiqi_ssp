#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/2

@author: Jay
"""
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from utils.crypto.beiqi_sign import client_sign_wapper
from db.db_oper import DBBeiqiSspInst
from setting import DB_TBL_ETICKET


ETICKET_STAT = [
    ETS_DISABLE,
    ETS_ENABLE,
    ETS_CHECKED,
] = xrange(0, 3)


@route(r'/eticket/check')
class ETicketCheckHandler(HttpRpcHandler):
    @web_adaptor()
    @client_sign_wapper()
    def get(self, user_name, code, *args, **kwargs):
        sql = "SELECT * FROM {tbl} where code='{code}' limit 1".format(tbl=DB_TBL_ETICKET, code=code)
        logger.debug('ETicketCheckHandler select::user=%r, code=%r, sql=%r' % (user_name, code, sql))
        ret_list = DBBeiqiSspInst.query(sql)
        if not ret_list:
            return {"status": 1}

        stat = int(ret_list[0]['stat'])
        if stat == ETS_DISABLE:
            return {"status": 2}

        if stat == ETS_CHECKED:
            return {"status": 3}

        sql = "UPDATE {tbl} SET stat={stat} WHERE code='{code}'".format(tbl=DB_TBL_ETICKET, stat=ETS_CHECKED, code=code)
        logger.debug('ETicketCheckHandler update::user=%r, code=%r, sql=%r' % (user_name, code, sql))
        DBBeiqiSspInst.query(sql)
        return {"status": 0}


@route(r'/eticket/add')
class ETicketAddHandler(HttpRpcHandler):
    @web_adaptor()
    @client_sign_wapper()
    def get(self, user_name, code, *args, **kwargs):
        sql = "SELECT * FROM {tbl} where code='{code}' limit 1".format(tbl=DB_TBL_ETICKET, code=code)
        logger.debug('ETicketAddHandler select::user=%r, code=%r, sql=%r' % (user_name, code, sql))
        ret_list = DBBeiqiSspInst.query(sql)
        if ret_list:
            return {"status": 1}

        sql = "insert into {tbl} (code, stat) values ('{code}', {stat})".format(tbl=DB_TBL_ETICKET, code=code, stat=1)
        logger.debug('ETicketAddHandler insert::user=%r, code=%r, sql=%r' % (user_name, code, sql))
        DBBeiqiSspInst.query(sql)
        return {"status": 0}