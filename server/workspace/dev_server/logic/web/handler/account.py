#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/6

@author: Jay
"""
from random import randint
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from utils.crypto.beiqi_sign import client_sign_wapper
from util.redis_cmds.circles import *
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.mysql_pack import pack as mysql_pack
from util.convert import combine_redis_cmds
from db.db_oper import DBBeiqiSspInst
from config import GMQDispRdsInts, GDevRdsInts
from setting import DB_TBL_DEVICE_INFO, DB_TBL_GID_INFO


@route(r'/sign_in')
class SignInHandler(HttpRpcHandler):
    @web_adaptor()
    @client_sign_wapper()
    def get(self, user_name, sn, *args, **kwargs):
        sql = "SELECT 1 FROM {db_name} WHERE sn = '{sn}'".format(db_name=DB_TBL_DEVICE_INFO, sn=sn)
        ret_list = DBBeiqiSspInst.query(sql)
        if len(ret_list) == 0:
            return {'status': 1}

        gid = GDevRdsInts.send_cmd(*get_gid_of_sn(sn))
        primary = GDevRdsInts.send_cmd(*get_group_primary(gid)) if gid is not None else None
        if primary is None:
            # unbound
            if gid is None:
                # generate gid
                while True:
                    tmp_gid = str(randint(1,9))
                    tmp_gid = tmp_gid + ''.join([str(randint(0, 9)) for i in xrange(5)])

                    sn_of_gid = GDevRdsInts.send_cmd(*get_sn_of_gid(tmp_gid))
                    if sn_of_gid is None:
                        # tmp_pid is not used.
                        sql = 'select * from {db} WHERE gid = {gid}'.format(db=DB_TBL_GID_INFO, gid=tmp_gid)
                        query_result = DBBeiqiSspInst.query(sql)
                        if query_result and query_result[0].get('gid_kind') == 1:
                            # tmp_pid is a nice number
                            continue
                        gid = tmp_gid
                        GDevRdsInts.send_multi_cmd(*combine_redis_cmds(set_gid_of_sn(sn, tmp_gid), set_sn_of_gid(tmp_gid, sn)))
                        break
                #update mysql data
                GMQDispRdsInts.send_multi_cmd(*combine_redis_cmds(
                    shortcut_mq('gen_mysql', mysql_pack(DB_TBL_DEVICE_INFO, {'gid': gid}, action=2, ref_kvs={'sn': sn})),
                    shortcut_mq('gen_mysql', mysql_pack(DB_TBL_GID_INFO, {'sn': sn, 'status': 'used'}, action=2, ref_kvs={'gid': gid}))
                ))

            ic = GDevRdsInts.send_cmd(*get_sn_ic(sn))
            if not ic:
                # no ic in storage.
                while True:
                    ic = ''.join([str(randint(0, 9)) for i in xrange(9)])
                    ic_exist = GDevRdsInts.send_cmd(*get_ic_sn(ic))
                    if not ic_exist:
                        break
            logger.debug('sign in, gid={0}, ic={1}'.format(gid, ic))
            GDevRdsInts.send_multi_cmd(*combine_redis_cmds(set_sn_ic(sn, ic), set_ic_sn(ic, sn)))

            return {'binding': 0, 'ic': ic, 'gid': gid, 'status': 0}
        else:
            logger.debug('sign in, pid={0}, sn={1}, binded'.format(gid, sn))
            return {'binding': 1, 'gid': gid, 'status': 0}