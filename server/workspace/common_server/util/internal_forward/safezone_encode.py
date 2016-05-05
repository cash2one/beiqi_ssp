#coding:utf-8


from . import prepend_head
from util.convert import redis_encode_batch, is_float


def zone_one(lat, log, radius, name):
    if isinstance(lat, str) and not is_float(lat):
        raise ValueError('lat invalid: %s' % lat)
    if isinstance(log, str) and not is_float(log):
        raise ValueError('log invalid: %s' % log)

    lat = float(lat)
    log = float(log)

    return {
        'lat': lat,
        'log': log,
        'radius': radius,
        'name': name
    }


@prepend_head
def zone_batch(pid, *zones):
    """
    需要注意火星坐标的问题，该打包函数不负责坐标系转换
    批量设置安全区

    :param zones: {
        'lat': 0,
        'log': 1,
        'radius': 2,
        'name': 'xx',
    }
    """
    params = ['zb', pid]
    for z in zones:
        params.append(z.get('lat'))
        params.append(z.get('log'))
        params.append(z.get('radius'))
        params.append(z.get('name'))
    return redis_encode_batch(*params)


@prepend_head
def zone_event(pid, lat, log, ts, road, token, battery, low_power, *wifis):
    """
    投递定位事件
    需要注意火星坐标问题，该函数默认为火星坐标
    :param battery: 电池电量
    :param token: 定位事件token
    :param log:
    :param lat:
    :param pid: 设备id
    :param ts: 定位事件时间,int
    :param road: 道路名
    :param low_power: 是否低电量
    :param wifis: wifi列表
    """
    if not (pid and isinstance(pid, str)):
        raise ValueError('pid not str: %s' % type(pid))
    if not (lat and isinstance(lat, float) and log and isinstance(log, float)):
        raise ValueError('lat or log not float: %s, %s' % (type(lat), type(log)))
    if not (ts and isinstance(ts, (int, long, float))):
        raise ValueError('ts not int: %s' % (type(ts)))
    if not isinstance(road, str):
        raise ValueError('road not str: %s' % type(road))
    if not (token and isinstance(token, (int, long))):
        raise ValueError('token not int: %s' % type(token))

    return redis_encode_batch('ze', pid, lat, log, ts, road, token, battery, low_power, *wifis)