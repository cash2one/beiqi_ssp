#coding:utf-8


from random import shuffle
from util.redis.async_redis.redis_resp import decode_resp_ondemand
from util.convert import is_num
from itertools import izip
import time
import random


REC_MANIFEST_KEYS = ('ts', 'len', 'fn', 'r', 'user_cmd')


def _rec_mnf_key(pid, token):
    return ':'.join((pid, token, time.strftime('%Y%m%d')))


def _query_multi(mem_client, keys):
    values = mem_client.get_multi(keys.keys())
    for k, v in values.iteritems():
        if not v:
            continue
        ok, v, _ = decode_resp_ondemand(v, 0, 0, 1)
        if not ok:
            continue
        yield k, dict(izip(REC_MANIFEST_KEYS, v))


def multi_rec_mnf(pid, mem_client, *tokens):
    """
    多个录音摘要
    """
    #查询key和token的映射关系
    keys = dict(((_rec_mnf_key(pid, x), x) for x in tokens if is_num(x)))
    d = dict(_query_multi(mem_client, keys))
    for k, v in keys.iteritems():
        _ = d.pop(k, None)
        if not _:
            continue
        d.update({v: _})
    return d


def single_rec_mnf(pid, mem_client, token):
    """
    单个录音摘要
    :param pid:
    :param mem_client:
    :param token:
    :return:
    """
    if not is_num(token):
        return None

    values = mem_client.get(_rec_mnf_key(pid, token))
    if not values:
        return None
    ok, values, _ = decode_resp_ondemand(values, 0, 0, 1)
    if not ok:
        return None
    return dict(izip(REC_MANIFEST_KEYS, values))


