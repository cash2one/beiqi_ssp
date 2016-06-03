#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/12

@author: Jay
"""
import time
import json
from util.redis_cmds.circles import get_group_primary, get_sn_of_gid, get_gid_of_sn, get_user_groups, get_group_followers
from util.sso.moments import add_share, save_share_info, add_self_share
from utils import logger
from mq_packs.uni_pack import shortcut_mq
from mq_packs.cloud_push_pack import pack as push_pack
from util.user import get_user_gids, is_app_user


def should_send_ios(user, file_type):
    """
    是否发送ios推送，推送所有类型消息
    :param user: 用户
    :param file_type:  文件类型
    :return:
    """
    push_params = redis_cal.send_cmd('get', ':'.join(('account', user)))
    platform = ""
    if push_params:
        push_params = push_params.split(':')
        platform, ver = push_params[:2]
    return ('ios' == platform or int(file_type) != 3) and is_app_user(user)


def msg_2_ios(author, type, files, text=''):
    gid_list = get_user_gids(author, dev_filter)
    logger.debug('msg_2_ios:: gid_list=%r, author=%r', gid_list, author)

    share_to = ''
    location = ''

    resp = {}
    accounts = set([])
    ts = float('%0.2f' % time.time())
    for gid in gid_list:
        primary_account = dev_filter.send_cmd(*get_group_primary(gid))
        if primary_account is None:
            return json.dumps({'status': 1})

        share_id = ':'.join(('share', str(ts), gid, author))
        dev_filter.send_cmd(*add_self_share(author, ts, share_id))
        dev_filter.send_cmd(*save_share_info(share_id, author, gid, share_to, location, text, type, files, come_from='wechat'))

        accounts.update(dev_filter.send_cmd(*get_group_followers(gid)))
        accounts.add(primary_account)
        accounts.add(dev_filter.send_cmd(*get_sn_of_gid(gid)))
        resp[gid] = {'share_id': share_id}

    send_accounts = filter(lambda u: u != author and should_send_ios(u, type), accounts)
    logger.debug('msg_2_ios, send_accounts={0}'.format(send_accounts))

    for acc in send_accounts:
        dev_filter.send_cmd(*add_share(acc, share_id, ts))
        mq_hub.send_cmd(
                *shortcut_mq(
                    'cloud_push',
                    # sourcer, cb, from, description
                    push_pack(author, 'share', 2, ':'.join((share_id, text, type, files)), account=acc)
                )
            )
    return resp

