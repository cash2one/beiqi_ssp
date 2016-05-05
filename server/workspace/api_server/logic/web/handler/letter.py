#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/4

@author: Jay
"""
import time
import ujson
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from util.sso.account import exist_account, set_account_pwd
from util.convert import bs2utf8, is_email
from util.redis_cmds.circles import get_dev_primary
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.cloud_push_pack import pack as push_pack
from util.redis_cmds.letters import *
from api_server.config import GDevRdsInts, GAccRdsInts, GMQDispRdsInts
from api_server.db.db_oper import DBBeiqiSspInst


@route(r'/delete_letter')
class DelLetterHandler(HttpRpcHandler):
    @web_adaptor()
    def post(self, Username, letter_id):
        GDevRdsInts.pipe_execute((del_letter_info(letter_id), del_letter_inbox(Username, letter_id)))
        return {'status': 0}


@route(r'/receive_letter')
class ReceiveLetterHandler(HttpRpcHandler):
    @web_adaptor()
    def post(self, Username, start=None, end=None):
        if (start and end) is None:
            return {'status': 1}

        letter_ids_list = GDevRdsInts.execute([get_letter_inbox(Username, start, end)])
        if len(letter_ids_list) == 0:
            return {'status': 2}

        ret = {}
        for letter_id in letter_ids_list:
            letter_info = GDevRdsInts.execute([get_letter_info(letter_id)])
            ret[letter_id] = letter_info
        return ret


@route(r'/send_letter')
class SendLetterHandler(HttpRpcHandler):
    @web_adaptor()
    def post(self, Username, receivers, duplicate_to, topic, text, type, files):
        ts = float('%0.2f' % time.time())
        letter_id = ':'.join(('letter', str(ts), Username, receivers))

        GDevRdsInts.execute([save_letter_info(letter_id, ':'.join((topic, text, type, files)))])
        GDevRdsInts.execute([add_letter_outbox(Username, letter_id, ts)])

        receivers = ujson.loads(receivers)
        logger.debug('receivers={0}'.format(receivers))
        acc_noexist_list = []
        for acc in receivers:
            acc = bs2utf8(acc)

            account_exist = GAccRdsInts.execute([exist_account(acc)])
            if not account_exist:
                # not in redis, check mysql
                sql = 'select * from {0} where username=%s'.format('ssp_user_login')
                res = DBBeiqiSspInst.query(sql, acc)
                if len(res) == 0:
                    # not in mysql, so we check if it's a sn
                    if not is_email(acc):
                        primary = GDevRdsInts.execute([get_dev_primary(acc)])
                        if not primary:
                            # no primary, illegal
                            logger.debug('acc={0} not exist'.format(acc))
                            acc_noexist_list.append(acc)
                            continue
                else:
                    # exist in mysql, so we cache it in redis
                    pwd = res[0].get('password').encode('utf8')
                    GAccRdsInts.execute([set_account_pwd(acc, pwd)])

            GDevRdsInts.execute([add_letter_inbox(acc, letter_id, ts)])
            GMQDispRdsInts.execute(
                [shortcut_mq(
                    'cloud_push',
                    # sourcer, cb, from, description
                    push_pack(Username, 'letter', 2, ':'.join((letter_id, topic, text, type, files)), account=acc)
                )]
            )

        return acc_noexist_list