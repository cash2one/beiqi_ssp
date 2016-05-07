#coding:utf8
import ujson
import time
from utils import logger
from utils.network.http import HttpRpcClient
from util.convert import bs2utf8, combine_redis_cmds
from util.redis_cmds.circles import get_group_primary, test_user_follow_group
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.cloud_push_pack import pack as push_pack
from util.mq_packs.mysql_pack import pack as mysql_pack
from util.redis_cmds.user_info import set_user_group_msglist, set_user_info
from util.redis_cmds.circles import set_user_nickname
from util.redis_cmds.wechat import get_wechat_access_token
from config import GDevRdsInts, GMQDispRdsInts
from setting import wechat_userinfo_url


user_info_tbl = 'user_info'


wechat_reply_template = \
{
    1: '请求已发送，等待主账号同意',
    3: '设备不存在,请重新输入',
    7: '输入的亲友圈ID长度不符',
    8: '该ID已经关注',
    9: '主账号不能重复关注'
}


def get_userinfo(username):
    # remove wx# prefix
    username = username[3:]
    token = GDevRdsInts.send_cmd(*get_wechat_access_token())
    url = wechat_userinfo_url.format(token, username)
    user_info = HttpRpcClient().fetch_async(url=url)
    return ujson.loads(user_info.body)


def add_device(username, code, user_info=None):
    primary = GDevRdsInts.send_cmd(*get_group_primary(code))
    if not primary:
        return {'status': 3}

    if username == primary:
        return {'status': 9}

    following = GDevRdsInts.send_cmd(*test_user_follow_group(username, code))
    if following:
        return {'status': 8}

    payload = ujson.dumps({'applicant': username, 'pid': code, 'msg': '', 'file': '', 'time': str(time.time())})

    # put follow request into primary msglist
    GDevRdsInts.send_multi_cmd(*combine_redis_cmds(set_user_group_msglist(primary, code, 'follow', payload)))

    # set user info
    if user_info is None:
        user_info = get_userinfo(username)

    nickname = bs2utf8(user_info.get('nickname'))
    user_info = ujson.dumps(user_info)
    GDevRdsInts.send_cmd(*set_user_info(username, user_info))
    GDevRdsInts.send_cmd(*set_user_nickname(username, nickname))

    GMQDispRdsInts.send_cmd(
        *shortcut_mq('gen_mysql',
            mysql_pack(user_info_tbl,
                       {'nickname': nickname},
                        action=2,
                        ref_kvs={'username': username}
            )
        )
    )
    logger.debug('set user info, username={0}, user_info={1}'.format(username, user_info))

    GMQDispRdsInts.send_cmd(
        # sourcer, cb, from, description
        *shortcut_mq('cloud_push', push_pack(username, 'follow', 2, payload, account=primary))
    )

    logger.debug('follow, acc={0}, followee={1}, msg={2}, file={3}'.format(username, code, '', ''))
    return {'status': 1}
