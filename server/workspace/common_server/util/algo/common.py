#coding:utf-8


import re
from util.convert import is_mac, is_num


__algo_day_pattern = re.compile(r'^[1-7](?:,[1-7])*$')
__in_out_ts_pattern = re.compile(r'^\d{3,4}$')


def algodays_us(v):
    """
    算法的有效天转换
    """
    if not (v and isinstance(v, str) and __algo_day_pattern.search(v)):
        raise ValueError('algo days invalid: {0}'.format(v))

    days = 0
    for x in (int(x) - 1 for x in v.split(',')):
        days |= (1 << x)
    return days


def algo_inoutts_us(v):
    """
    算法进出时间转化
    """
    if not (v and isinstance(v, str) and __in_out_ts_pattern.search(v)):
        raise ValueError('in_out_ts invalid: {0}'.format(v))
    v = int(v)
    if not 0 <= v <= 2359:
        raise ValueError('in_out_ts out out scope: {0}'.format(v))
    return v


def algo_wifi_rssi_us(v):
    if not is_num(v):
        raise ValueError('wifi rssi invalid: {0}'.format(v))
    return int(v)


def conv_mac(mac):
    """
    字符串mac地址转换为6字节long型
    """
    if not is_mac(mac):
        raise ValueError('mac invalid: %r' % mac)

    bs = (int(x, 16) for x in mac.split(':'))
    r = 0
    for i, b in enumerate(bs):
        r |= b << (i * 8)
    return r


def conv_wifi_rssi(rssi):
    if not (isinstance(rssi, int) and rssi < 0):
        raise ValueError('wifi rssi invalid: %r' % rssi)
    return rssi + 100


def conv_base_rssi(rssi):
    if not (isinstance(rssi, int) and rssi < 0):
        raise ValueError('base wifi invalid: %r' % rssi)
    return rssi + 113