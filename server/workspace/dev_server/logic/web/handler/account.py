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
from utils.crypto.beiqi_sign import beiqi_tk_sign_wapper
from util.redis_cmds.circles import *
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.mysql_pack import pack as mysql_pack
from dev_server.db.db_oper import DBBeiqiSspInst
from dev_server.config import GMQDispRdsInts, GDevRdsInts


devinfo_tbl_name = 'device_info'
gidinfo_tbl_name = 'gid_info'


@route(r'/sign_in')
class SignInHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, sn):
        sql = 'SELECT 1 FROM {0} WHERE sn = %s'.format(devinfo_tbl_name)
        ret_list = DBBeiqiSspInst.query(sql, sn)
        if len(ret_list) == 0:
            return {'status': 1}

        gid = GDevRdsInts.execute([get_gid_of_sn(sn)])
        primary = GDevRdsInts.execute([get_group_primary(gid)]) if gid is not None else None
        if primary is None:
            # unbound
            if gid is None:
                # generate gid
                while True:
                    tmp_gid = str(randint(1,9))
                    tmp_gid = tmp_gid + ''.join([str(randint(0, 9)) for i in xrange(5)])

                    sn_of_gid = GDevRdsInts.execute([get_sn_of_gid(tmp_gid)])
                    if sn_of_gid is None:
                        # tmp_pid is not used.
                        sql = 'select * from {0} WHERE gid = %s'.format(gidinfo_tbl_name)
                        query_result = DBBeiqiSspInst.query(sql, tmp_gid)
                        if query_result[0].get('gid_kind') == 1:
                            # tmp_pid is a nice number
                            continue
                        gid = tmp_gid
                        GDevRdsInts.pipe_execute((set_gid_of_sn(sn, tmp_gid), set_sn_of_gid(tmp_gid, sn)))
                        break
                #update mysql data
                GMQDispRdsInts.pipe_execute((
                    shortcut_mq('gen_mysql', mysql_pack(devinfo_tbl_name, {'gid': gid}, action=2, ref_kvs={'sn': sn})),
                    shortcut_mq('gen_mysql', mysql_pack(gidinfo_tbl_name, {'sn': sn, 'status': 'used'}, action=2, ref_kvs={'gid': gid}))
                ))

            ic = GDevRdsInts.execute([get_sn_ic(sn)])
            if not ic:
                # no ic in storage.
                while True:
                    ic = ''.join([str(randint(0, 9)) for i in xrange(9)])
                    ic_exist = GDevRdsInts.execute([get_ic_sn(ic)])
                    if not ic_exist:
                        break
            logger.debug('sign in, gid={0}, ic={1}'.format(gid, ic))
            GDevRdsInts.pipe_execute((set_sn_ic(sn, ic), set_ic_sn(ic, sn)))

            return {'binding': 0, 'ic': ic, 'gid': gid, 'status': 0}
        else:
            logger.debug('sign in, pid={0}, sn={1}, binded'.format(gid, sn))
            return {'binding': 1, 'gid': gid, 'status': 0}