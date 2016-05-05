# coding: utf-8

# IC_USING_SET = 'ic_using_set'
# PID_USING_SET = 'pid_using_set'
DEV_PRIMARY_ACCOUNT = 'dev_primary'
USER_DEV_SET = 'user_dev_set'
USER_GROUP_SET = 'user_group_set'
DEV_FOLLOWERS = 'dev_followers'
SN_GID_MAPPING = 'sn_2_gid'
# to decide if pid is in use.
GID_SN_MAPPING = 'gid_2_sn'
USER_INFO_SIMPLIFIED = 'user_info_simplified'
OCCUPIED_NICKNAME = 'occupied_nickname'
INVITE_FOLLOW_SET = 'invite_follow_set'
DEV_TK_TIME = 'dev_tk_time'

GROUP_PRIMARY_ACCOUNT = 'group_primary'
GROUP_FOLLOWERS = 'group_followers'

WECHAT_USER_DEVS = 'wechat_user_devs'

SN_2_IC = 'sn_2_ic'
IC_2_SN = 'ic_2_sn'


def set_tk_time(sn, ts):
    return 'hset', DEV_TK_TIME, sn, ts


def get_tk_time(sn):
    return 'hget', DEV_TK_TIME, sn


def get_gid_of_sn(sn):
    return 'hget', SN_GID_MAPPING, sn


def set_gid_of_sn(sn, gid):
    return 'hset', SN_GID_MAPPING, sn, gid


def del_gid_of_sn(sn):
    return 'hdel', SN_GID_MAPPING, sn


def set_ic_sn(ic, sn):
    return 'hsetnx', IC_2_SN, ic, sn


def get_ic_sn(ic):
    return 'hget', IC_2_SN, ic


def del_ic_sn(ic):
    return 'hdel', IC_2_SN, ic


def set_sn_ic(sn, ic):
    assert sn and isinstance(sn, str)
    assert ic and isinstance(ic, str) and len(ic) == 9

    return 'hset', SN_2_IC, sn, ic


def get_sn_ic(sn):
    assert sn and isinstance(sn, str)

    return 'hget', SN_2_IC, sn


def del_sn_ic(sn):
    return 'hdel', SN_2_IC, sn


def get_sn_of_gid(gid):
    assert gid and isinstance(gid, str)

    return 'hget', GID_SN_MAPPING, gid


def set_sn_of_gid(gid, sn):
    assert gid and isinstance(gid, str)

    return 'hsetnx', GID_SN_MAPPING, gid, sn


def del_sn_of_gid(gid):
    return 'hdel', GID_SN_MAPPING, gid


def test_nickname(nickname):
    assert nickname and isinstance(nickname, str)

    return 'sismember', OCCUPIED_NICKNAME, nickname


def get_user_nickname(acc):
    assert acc and isinstance(acc, str)

    return 'hget', ':'.join((USER_INFO_SIMPLIFIED, acc)), 'nickname'


def set_user_nickname(acc, nickname):
    return 'hset', ':'.join((USER_INFO_SIMPLIFIED, acc)), 'nickname', nickname


def get_dev_primary(sn):
    assert sn and isinstance(sn, str)

    return 'hget', DEV_PRIMARY_ACCOUNT, sn


def get_group_primary(gid):
    return 'hget', GROUP_PRIMARY_ACCOUNT, gid


def get_group_followers(gid):
    return 'smembers', ':'.join((GROUP_FOLLOWERS, gid))


def get_dev_followers(sn):
    assert sn and isinstance(sn, str)

    return 'smembers', ':'.join((DEV_FOLLOWERS, sn))


def test_user_follow_group(user, gid):
    return 'sismember', ':'.join((GROUP_FOLLOWERS, gid)), user

# def test_user_follow_dev(user, sn):
#     assert user and isinstance(user, str)
#     assert sn and isinstance(sn, str)
#
#     return 'sismember', ':'.join((DEV_FOLLOWERS, sn)), user


def get_user_devs(acc):
    assert acc and isinstance(acc, str)

    return 'smembers', ':'.join((USER_DEV_SET, acc))


def get_user_groups(acc):

    return 'smembers', ':'.join((USER_GROUP_SET, acc))
#
# def bind_dev_primary(sn, primary):
#     assert sn and isinstance(sn, str)
#     assert primary and isinstance(primary, str)
#
#     return ('hsetnx', DEV_PRIMARY_ACCOUNT, sn, primary), \
#            ('sadd', ':'.join((USER_DEV_SET, primary)), sn)
def set_group_primary(gid, primary):
    return 'hsetnx', GROUP_PRIMARY_ACCOUNT, gid, primary


def del_group_primary(gid):
    return 'hdel', GROUP_PRIMARY_ACCOUNT, gid

def bind_group_primary(gid, sn, primary):

    return ('hsetnx', GROUP_PRIMARY_ACCOUNT, gid, primary), \
           ('hsetnx', DEV_PRIMARY_ACCOUNT, sn, primary), \
           ('sadd', ':'.join((GROUP_FOLLOWERS, gid)), primary), \
           ('sadd', ':'.join((USER_DEV_SET, primary)), sn), \
           ('sadd', ':'.join((USER_GROUP_SET, primary)), gid)



def unbind_group_primary(gid, sn, primary):

    return ('hdel', GROUP_PRIMARY_ACCOUNT, gid), \
           ('srem', ':'.join((GROUP_FOLLOWERS, gid)), primary), \
           ('srem', ':'.join((USER_DEV_SET, primary)), sn), \
           ('hdel', DEV_PRIMARY_ACCOUNT, sn), \
           ('srem', ':'.join((USER_GROUP_SET, primary)), gid)


# def unbind_dev_primary(sn, primary):
#
#     return ('hdel', DEV_PRIMARY_ACCOUNT, sn), \
#            ('srem', ':'.join((USER_DEV_SET, primary)), sn)
def follow_group(gid, sn, acc):
    return ('sadd', ':'.join((GROUP_FOLLOWERS, gid)), acc), \
           ('sadd', ':'.join((USER_DEV_SET, acc)), sn), \
           ('sadd', ':'.join((USER_GROUP_SET, acc)), gid)

# def follow_dev(sn, acc):
#     assert sn and isinstance(sn, str)
#     assert acc and isinstance(acc, str)
#
#     return ('sadd', ':'.join((DEV_FOLLOWERS, sn)), acc), \
#            ('sadd', ':'.join((USER_DEV_SET, acc)), sn)
def unfollow_group(gid, sn, acc):
    assert sn and isinstance(sn, str)
    assert acc and isinstance(acc, str)

    return ('srem', ':'.join((GROUP_FOLLOWERS, gid)), acc), \
           ('srem', ':'.join((USER_DEV_SET, acc)), sn), \
           ('srem', ':'.join((USER_GROUP_SET, acc)), gid)

# def unfollow_dev(sn, acc):
#     assert sn and isinstance(sn, str)
#     assert acc and isinstance(acc, str)
#
#     return ('srem', ':'.join((DEV_FOLLOWERS, sn)), acc), \
#            ('srem', ':'.join((USER_DEV_SET, acc)), sn)


def set_invite_follow(gid, master, guest):
    assert gid and isinstance(gid, str)
    assert master and isinstance(master, str)
    assert guest and isinstance(guest, str)

    return 'sadd', ':'.join((INVITE_FOLLOW_SET, gid, master)), guest


def del_invite_follow(gid, master, guest):
    assert gid and isinstance(gid, str)
    assert master and isinstance(master, str)
    assert guest and isinstance(guest, str)

    return 'srem', ':'.join((INVITE_FOLLOW_SET, gid, master)), guest


def ismember_invite_follow(gid, master, guest):
    assert gid and isinstance(gid, str)
    assert master and isinstance(master, str)
    assert guest and isinstance(guest, str)

    return 'sismember', ':'.join((INVITE_FOLLOW_SET, gid, master)), guest


def get_wechat_gids(wechat_username):
    return 'hkeys', ':'.join((WECHAT_USER_DEVS, wechat_username))

def getall_wechat_devs(wechat_username):
    return 'hgetall', ':'.join((WECHAT_USER_DEVS, wechat_username))


def hset_wechat_gid(wechat_username, gid, nickname=''):
    if not nickname:
        nickname = '平板' + gid
    return 'hset', ':'.join((WECHAT_USER_DEVS, wechat_username)), gid, nickname


def hdel_wechat_gid(wechat_username, gid):
    return 'hdel', ':'.join((WECHAT_USER_DEVS, wechat_username)), gid