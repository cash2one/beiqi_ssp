#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/6

@author: Jay
"""
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from util.redis_cmds.circles import hset_wechat_gid
from util.mq_packs.mysql_pack import pack as mysql_pack
from util.mq_packs.cloud_push_pack import pack as push_pack
from util.mq_packs.uni_pack import shortcut_mq
from util.convert import combine_redis_cmds
from util.redis_cmds.circles import unfollow_group, get_sn_of_gid, hdel_wechat_gid, get_group_followers, get_group_primary
from config import GDevRdsInts, GMQDispRdsInts
from setting import DB_TBL_USER_INFO


@route(r'/wechat/pages/user_guide')
class UserGuideHandler(HttpRpcHandler):
    @web_adaptor(use_http_render=False)
    def get(self, *args, **kwargs):
        self.render('wechat_user_guide.html')
        return


@route(r'/wechat/change_nickname')
class ChangeNicknameHandler(HttpRpcHandler):
    @web_adaptor()
    def get(self, new_nick, username, gid, *args, **kwargs):
        GDevRdsInts.send_cmd(*hset_wechat_gid(username, gid, new_nick))
        GMQDispRdsInts.send_cmd(
        *shortcut_mq('gen_mysql',
            mysql_pack(DB_TBL_USER_INFO,
                       {'nickname': new_nick},
                       action=2,
                       ref_kvs={'username': username}
                       )
            )
        )
        return


@route(r'/wechat/unbind')
class UnbindHandler(HttpRpcHandler):
    @web_adaptor(use_json_dumps=False)
    def get(self, username, gid, userinfo='', *args, **kwargs):
        sn = GDevRdsInts.send_cmd(*get_sn_of_gid(gid))

        logger.debug('username = %r, gid = %r, sn = %r, userinfo = %r', username, gid, sn, userinfo)
        GDevRdsInts.send_cmd(*hdel_wechat_gid(username, gid))
        GDevRdsInts.send_multi_cmd(*combine_redis_cmds(unfollow_group(gid, sn, username)))

        accounts = GDevRdsInts.send_cmd(*get_group_followers(gid))
        logger.debug('share, accounts={0}'.format(accounts))
        # accounts is set object
        primary_account = GDevRdsInts.send_cmd(*get_group_primary(gid))

        accounts.add(primary_account)
        sn = GDevRdsInts.send_cmd(*get_sn_of_gid(gid))
        accounts.add(sn)

        logger.debug('share, accounts={0}'.format(accounts))

        for acc in accounts:
            if acc[:3] == 'wx#':
                continue

            GMQDispRdsInts.send_cmd(
                    *shortcut_mq(
                        'cloud_push',
                        # sourcer, cb, from, description
                        push_pack(username, 'unfollow', 2, ':'.join((username, gid)), account=acc)
                    )
                )
        return 'success'