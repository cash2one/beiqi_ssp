#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/6

@author: Jay
"""
import ujson
from utils import logger
from util.convert import bs2utf8
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.mysql_pack import pack as mysql_pack

def build_mq_package(acc, sn, dev_type, payload):
    """
    构建mq包文
    :param bs_list:
    :param dev_sn:
    :param log_ob:
    :param payload:
    :param pid:
    :param raw_plain:
    """
    ts = payload.get('ts')
    loc = payload.get('loc')
    logger.debug('loc v1, loc=%r' % loc)
    loc = ujson.loads(loc)
    loc = dict(map(lambda x:(x[0].encode('utf8'), x[1].encode('utf8')) if isinstance(x[1], basestring) else (x[0].encode('utf8'), x[1]), loc.items()))
    logger.debug('after, loc v1 loc=%r' % loc)
    loc['sn'] = sn
    loc['src_ts'] = ts
    loc['dev_type'] = dev_type

    battery = payload.get('battery')
    charge = payload.get('charge')
    soft_ver = bs2utf8(payload.get('soft_version'))

    yield shortcut_mq('gen_mysql', mysql_pack(
        'location',
        loc,
        0,
        None,
        'src_ts'))

    yield shortcut_mq('gen_mysql', mysql_pack(
        'dev_state',
        {'src_ts': ts, 'sn': sn, 'battery': battery, 'charge': charge, 'soft_ver': soft_ver, 'dev_type': dev_type},
        0,
        None,
        'src_ts'
    ))