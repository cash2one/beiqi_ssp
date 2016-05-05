# coding: utf-8

import time

USER_INFO_MAPPING = 'user_info_mapping'
USER_SN_MSGS = 'user_sn_msgs'
USER_SYSTEM_MSGS = 'user_system_msgs'
GEO_FENCES = 'geo_fences'
NICE_GID_MAPPING = 'nice_gid_mapping'
OLD_GID_MAPPING = 'old_gid_mapping'

def set_user_info(username, payload):
    assert username and isinstance(username, str)
    assert payload and isinstance(payload, str)

    return 'hset', USER_INFO_MAPPING, username, payload


def get_user_info(username):
    assert username and isinstance(username, str)

    return 'hget', USER_INFO_MAPPING, username


def set_user_group_msglist(username, gid, action, msg):
    assert username and isinstance(username, str)
    assert gid and isinstance(gid, str)
    assert msg and isinstance(msg, str)
    # list index begins from left with 0
    now = str(time.time())
    return ('lpush', ':'.join((USER_SN_MSGS, username, gid)), ':'.join((now, action, msg))), \
           ('ltrim', ':'.join((USER_SN_MSGS, username, gid)), 0, 20)


def get_user_group_msglist(username, gid):
    assert username and isinstance(username, str)

    return 'lrange', ':'.join((USER_SN_MSGS, username, gid)), 0, 20


def set_user_system_msglist(username, action, msg):
    assert username and isinstance(username, str)
    assert msg and isinstance(msg, str)
    # list index begins from left with 0
    now = str(time.time())
    return ('lpush', ':'.join((USER_SYSTEM_MSGS, username)), ':'.join((now, action, msg))), \
           ('ltrim', ':'.join((USER_SYSTEM_MSGS, username)), 0, 20)


def get_user_system_msglist(username):
    assert username and isinstance(username, str)

    return 'lrange', ':'.join((USER_SYSTEM_MSGS, username)), 0, 20


def save_geo_fence(pid, creator, lon, lat, rad, name):

    return 'hset', ':'.join((GEO_FENCES, pid)), ':'.join((lon, lat, rad)), ':'.join((creator, name))


def del_geo_fence(pid, lon, lat, rad):

    return 'hdel', ':'.join((GEO_FENCES, pid)), ':'.join((lon, lat, rad))


def get_geo_fence(pid, lon, lat, rad):
    return 'hget', ':'.join((GEO_FENCES, pid)), ':'.join((lon, lat, rad))


def get_all_geo_fences(pid):
    assert pid and isinstance(pid, str)

    return 'hgetall', ':'.join((GEO_FENCES, pid))


def set_nice_gid(gid, nice_gid):
    return 'hset', NICE_GID_MAPPING, gid, nice_gid


def get_nice_gid(gid):
    return 'hget', NICE_GID_MAPPING, gid


def set_old_gid(nice_gid, old_gid):
    return 'hset', OLD_GID_MAPPING, nice_gid, old_gid


def get_old_gid(nice_gid):
    return 'hget', OLD_GID_MAPPING, nice_gid

