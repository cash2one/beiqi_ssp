from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from utils.crypto.beiqi_sign import beiqi_tk_sign_wapper
from util.mq_packs.mysql_pack import pack as mysql_pack
from util.mq_packs.uni_pack import shortcut_mq
from util.convert import bs2utf8
from util.redis_cmds.circles import get_sn_of_gid, set_sn_of_gid, set_gid_of_sn, get_group_primary, \
    set_group_primary, del_group_primary, del_sn_of_gid, get_group_followers, follow_group, get_user_nickname, set_user_nickname
from util.redis_cmds.user_info import set_nice_gid, get_user_info, set_user_info, set_old_gid, get_old_gid
from config import GDevRdsInts, GMQDispRdsInts


dev_info_tbl = 'device_info'
gid_info_tbl = 'gid_info'


@route(r'/map_nice_gid')
class MapNiceGidHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self):
        gid = bs2utf8(self.get_argument('gid'))
        nice_gid = bs2utf8(self.get_argument('nice_gid'))

        old_gid = GDevRdsInts.execute(get_old_gid(nice_gid))
        if old_gid:
            return {'status': 1}

        # sn & gid mapping
        sn = GDevRdsInts.execute(get_sn_of_gid(gid))
        if sn is None:
            sn = GDevRdsInts.execute(get_sn_of_gid(nice_gid))
            if sn is None:
                return {'status': 2}

        GDevRdsInts.pipe_execute((set_gid_of_sn(sn, nice_gid), set_sn_of_gid(nice_gid, sn), del_sn_of_gid(gid)))

        # gid & primary mapping
        primary = GDevRdsInts.execute(get_group_primary(gid))
        GDevRdsInts.pipe_execute((set_group_primary(nice_gid, primary), del_group_primary(gid)))

        followers = GDevRdsInts.execute(get_group_followers(gid))
        for follower in followers:
            GDevRdsInts.pipe_execute(follow_group(gid, sn, follower))

        GDevRdsInts.pipe_execute((set_nice_gid(gid, nice_gid), set_old_gid(nice_gid, gid)))
        user_info, nickname = GDevRdsInts.pipe_execute((get_user_info(gid), get_user_nickname(gid)))
        if user_info:
            GDevRdsInts.execute(set_user_info(nice_gid, user_info))
        if nickname:
            GDevRdsInts.execute(set_user_nickname(nice_gid, nickname))

        GMQDispRdsInts.pipe_execute((
                shortcut_mq('gen_mysql', mysql_pack(gid_info_tbl, {'sn': sn, 'status': 'used'}, action=2, ref_kvs={'gid': nice_gid})),
                shortcut_mq('gen_mysql', mysql_pack(dev_info_tbl, {'nice_gid': nice_gid}, action=2, ref_kvs={'sn': sn}))
            ))

        return {'status': 0}