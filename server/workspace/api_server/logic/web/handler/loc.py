#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/4

@author: Jay
"""
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from utils.crypto.beiqi_sign import client_sign_wapper
from util.redis_cmds.circles import *
from util.convert import mongo2utf8, combine_redis_cmds
from config import GDevRdsInts, GAccRdsInts
from db.db_oper import DBBeiqiSspInst


@route(r'/get_loc')
class GetLocHandler(HttpRpcHandler):
    @web_adaptor()
    @client_sign_wapper(GAccRdsInts)
    def get(self, user_name, sn, *args, **kwargs):
        """
        """
        expect_pa, sub_ok = GDevRdsInts.send_multi_cmd(*combine_redis_cmds(get_dev_primary(sn), test_user_follow_group(user_name, sn)))
        if not expect_pa:
            logger.warn('{0} not bound'.format(sn))
            self.set_status(400)
            return
        if not (expect_pa.split(':')[-1] == user_name or sub_ok):
            logger.warn('{0} not bound, not sa'.format(sn))
            self.set_status(400)
            return

        sql = "select longitude, latitude, altitude, accuracy, address, ad_code," \
              "src_ts as timestamp " \
              "from {db} where sn = '{sn}'" \
              "order by src_ts desc " \
              "limit 1"
        sql = sql.format(db='location', sn=sn)
        rec = DBBeiqiSspInst.query(sql)
        return mongo2utf8(rec[0]) if rec else {}