#conding:utf -8
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from util.mq_packs.mysql_pack import pack as mysql_pack
from util.mq_packs.uni_pack import shortcut_mq
from util.convert import combine_redis_cmds
from util.redis_cmds.circles import get_sn_of_gid, set_sn_of_gid, set_gid_of_sn, get_group_primary, \
    set_group_primary, del_group_primary, del_sn_of_gid, get_group_followers, follow_group, get_user_nickname, set_user_nickname
from util.redis_cmds.user_info import set_nice_gid, get_user_info, set_user_info, set_old_gid, get_old_gid
from config import GDevRdsInts, GMQDispRdsInts
from setting import DB_TBL_DEVICE_INFO, DB_TBL_GID_INFO


@route(r'/map_nice_gid')
class MapNiceGidHandler(HttpRpcHandler):
    @web_adaptor()
    def get(self, gid, nice_gid, *args, **kwargs):
        old_gid = GDevRdsInts.send_cmd(*get_old_gid(nice_gid))
        if old_gid:
            return {'status': 1}

        # sn & gid mapping
        sn = GDevRdsInts.send_cmd(*get_sn_of_gid(gid))
        if sn is None:
            sn = GDevRdsInts.send_cmd(*get_sn_of_gid(nice_gid))
            if sn is None:
                return {'status': 2}

        GDevRdsInts.send_multi_cmd(*combine_redis_cmds(set_gid_of_sn(sn, nice_gid), set_sn_of_gid(nice_gid, sn), del_sn_of_gid(gid)))

        # gid & primary mapping
        primary = GDevRdsInts.send_cmd(*get_group_primary(gid))
        GDevRdsInts.send_multi_cmd(*combine_redis_cmds(set_group_primary(nice_gid, primary), del_group_primary(gid)))

        followers = GDevRdsInts.send_cmd(*get_group_followers(gid))
        for follower in followers:
            GDevRdsInts.send_multi_cmd(*combine_redis_cmds(follow_group(gid, sn, follower)))

        GDevRdsInts.send_multi_cmd(*combine_redis_cmds(set_nice_gid(gid, nice_gid), set_old_gid(nice_gid, gid)))
        user_info, nickname = GDevRdsInts.send_multi_cmd(*combine_redis_cmds(get_user_info(gid), get_user_nickname(gid)))
        if user_info:
            GDevRdsInts.send_cmd(*set_user_info(nice_gid, user_info))
        if nickname:
            GDevRdsInts.send_cmd(*set_user_nickname(nice_gid, nickname))

        GMQDispRdsInts.send_multi_cmd(*combine_redis_cmds(
                shortcut_mq('gen_mysql', mysql_pack(DB_TBL_GID_INFO, {'sn': sn, 'status': 'used'}, action=2, ref_kvs={'gid': nice_gid})),
                shortcut_mq('gen_mysql', mysql_pack(DB_TBL_DEVICE_INFO, {'nice_gid': nice_gid}, action=2, ref_kvs={'sn': sn}))
            ))
        return {'status': 0}