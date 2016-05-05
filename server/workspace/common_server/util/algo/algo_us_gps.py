#coding:utf-8


from common import *


def convert(days, in_ts, out_ts, safe_level, lat, log, radius):
    """
    算法gps安全区转换
    :param days: 有效天
    :param in_ts: 进入时间
    :param out_ts: 离开时间
    :param lat: 北纬
    :param log: 东经
    """
    if not isinstance(safe_level, int):
        raise ValueError('gps safe_level not int, but %s' % type(safe_level))
    if not (isinstance(lat, float) and lat <= 90):
        raise ValueError('gps lat invalid: %r' % lat)
    if not (isinstance(log, float) and log <= 180):
        raise ValueError('gps log invalid: %r' % log)
    if not (radius and isinstance(radius, int)):
        raise ValueError('gps radius not int, but %s' % type(radius))

    d = {
        'days': algodays_us(days),
        'in_ts': algo_inoutts_us(in_ts),
        'out_ts': algo_inoutts_us(out_ts),
        'lat': int(lat * 23860929),
        'log': int(log * 11930000),
        'radius': radius,
    }

    if 3 == safe_level:
        d.update({'name': '学校'})
    if 6 == safe_level:
        d.update({'name': '家'})

    return d