#coding: utf8
import time
import ujson
from utils import logger
from util.redis_cmds.circles import get_group_primary, get_group_followers, get_sn_of_gid, get_wechat_gids
from util.sso.moments import add_share, save_share_info, add_self_share
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.cloud_push_pack import pack as push_pack
from config import GDevRdsInts, GMQDispRdsInts


def wechat_share(author, type, files):
    gid_list = GDevRdsInts.send_cmd(*get_wechat_gids(author))
    logger.debug('gid_list=%r, author=%r', gid_list, author)

    share_to = ''
    location = ''
    text = ''

    resp = {}
    for gid in gid_list:
        primary_account = GDevRdsInts.send_cmd(*get_group_primary(gid))
        if primary_account is None:
            return ujson.dumps({'status': 1})

        ts = float('%0.2f' % time.time())
        share_id = ':'.join(('share', str(ts), gid, author))
        GDevRdsInts.send_cmd(*add_self_share(author, ts, share_id))
        GDevRdsInts.send_cmd(*save_share_info(share_id, author, gid, share_to, location, text, type, files, come_from='wechat'))

        accounts = GDevRdsInts.send_cmd(*get_group_followers(gid))
        logger.debug('share, accounts={0}'.format(accounts))
        # accounts is set object
        accounts.add(primary_account)
        sn = GDevRdsInts.send_cmd(*get_sn_of_gid(gid))
        accounts.add(sn)

        logger.debug('share, accounts={0}'.format(accounts))

        for acc in accounts:
            if acc == author:
                continue
            GDevRdsInts.send_cmd(*add_share(acc, share_id, ts))

            GMQDispRdsInts.send_cmd(
                    *shortcut_mq(
                        'cloud_push',
                        # sourcer, cb, from, description
                        push_pack(author, 'share', 2, ':'.join((share_id, text, type, files)), account=acc)
                    )
                )

        resp[gid] = {'share_id': share_id}
    return resp
