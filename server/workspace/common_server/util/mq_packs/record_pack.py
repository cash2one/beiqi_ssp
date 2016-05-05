#coding:utf-8


import msgpack
from util.id_conv import rawid_tuple


def pack(pid, src_ts, reason, user_cmd, cmd_ord, cur_state, rec_ts, rec_len, rec_tot, rec_uid, redis_key):
    return msgpack.packb({
        'id': pid,
        'r': {
            'src_ts': src_ts,
            'reason': reason,
            'dev_id': rawid_tuple(pid)[2],
            'user_cmd': user_cmd,
            'cmd_ord': cmd_ord,
            'cur_state': cur_state,
            'rec_ts': rec_ts,
            'rec_len': rec_len,
            'rec_tot': rec_tot,
            'rec_uid': rec_uid,
            'redis_key': redis_key,
        }
    }, use_bin_type=True)