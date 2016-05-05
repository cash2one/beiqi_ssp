# coding:utf-8


import time
from types import NoneType

import msgpack

from util.id_conv import rawid_tuple
from util.convert import is_mac


def wifi_pack(mac, rssi, ssid):
    """
    wifi包
    :param ssid: like TPLink
    """
    if not is_mac(mac):
        raise ValueError('mac invalid: {0}'.format(mac))
    if not isinstance(rssi, int):
        raise ValueError('rssi not int: %s' % type(rssi))
    if not (ssid and isinstance(ssid, str)):
        raise ValueError('ssid not str: %s' % type(ssid))
    return {'mac': mac, 'rssi': rssi, 'ssid': ssid}


def cdmabs_pack(sid, nid, bsid, rssi, log=0, lat=0, mcc=460):
    """
    cdma基站数据包
    mcc 460表示天朝
    
    :param sid: 系统识别码
    :param log: 东经
    :param lat: 北纬
    """
    if not isinstance(rssi, int):
        raise ValueError('rssi not int: %s' % type(rssi))

    return {
        'mcc': mcc,
        # 电信
        'mnc': 3,
        'sid': sid,
        'nid': nid,
        'bsid': bsid,
        'log': log,
        'lat': lat,
        'rssi': rssi,
    }


def gsmbs_pack(lac, cellid, rssi, mnc, mcc=460):
    """
    gsm基站数据包
    mcc 460表示天朝
    """
    if not isinstance(rssi, int):
        raise ValueError('rssi not int: %s' % type(rssi))
    if not isinstance(mnc, int):
        raise ValueError('mnc not int: %s' % type(mnc))

    return {
        'mcc': mcc,
        'mnc': mnc,
        'lac': lac,
        'cellid': cellid,
        'rssi': rssi,
    }


def gps_pack(longitude, latitude, radius, gps_ts, altitude=0):
    """
    :param radius: 定位半径
    :param latitude: 北纬
    :param longitude: 东经
    :param altitude: 海拔
    :param gps_ts: gps芯片时间，如未定位成功则为0
    """
    if not isinstance(radius, int):
        raise ValueError('radius not int: %s' % radius)
    if not isinstance(longitude, (NoneType, float)):
        raise ValueError('longitude invalid: %s' % longitude)
    if not isinstance(latitude, (NoneType, float)):
        raise ValueError('latitude invalid: %s' % latitude)
    if not ((gps_ts is None) or isinstance(gps_ts, int)):
        raise ValueError('gps_ts invalid: %s' % gps_ts)

    if gps_ts is None:
        gps_ts = int(time.time())

    return {
        'lati': latitude,
        'log': longitude,
        'range': radius,
        'altitude': altitude,
        'gps_ts': gps_ts,
        'from': 1
    }


def pack_entry(rawid, user_cmd, token, gps_dict,
               wifi_list, bs_list,
               battery, svr_ts, loc_reason,
               dev_state = 0,
               steps = 0,
               cur_move_state = 0,
               push_pack=None,
               charge=0,
               fix_bs_loc=None):
    """
    :param loc_reason: 定位原因
    :param svr_ts: 服务器时间
    :param charge: 是否充电
    :param battery: 电池电量
    :param bs_list: 基站列表对象
    :param wifi_list: wifi列表对象
    :param gps_dict:
    :param user_cmd:
    :param rawid: 设备id
    :param token: 触发设备定位序号，例如PT30短信序号
    :param dev_state: 设备当前状态
    :param steps: 总步数
    :param cur_move_state:当前移动状态
    :param push_pack: push打包体，字符串格式
    :param fix_bs_loc: 需矫正的基站坐标，北纬，东经
    :param
    """
    if not (rawid and isinstance(rawid, str) and 8 == len(rawid)):
        raise ValueError('rawid invalid: %s' % rawid)
    if not isinstance(user_cmd, str):
        raise ValueError('user_cmd not str: %s' % type(user_cmd))
    if not (token and isinstance(token, int)):
        raise ValueError('token not int: %s' % type(token))
    if not isinstance(battery, int):
        raise ValueError('battery not int: %s' % type(battery))
    if push_pack:
        if not isinstance(push_pack, str):
            raise ValueError('push_pack not str: %s' % type(push_pack))
    if not isinstance(svr_ts, int):
        raise ValueError('svr_ts not int: %s' % svr_ts)
    if not isinstance(loc_reason, int):
        raise ValueError('loc_reason not int: %s' % loc_reason)

    rawid = rawid_tuple(rawid)
    if not rawid:
        return None

    wifi_list = wifi_list or ()
    bs_list = bs_list or ()
    if not isinstance(wifi_list, (list, tuple)):
        wifi_list = (wifi_list,)
    if not isinstance(bs_list, (list, tuple)):
        bs_list = (bs_list,)

    return msgpack.packb(
        {
            'dev_id': rawid,
            'user_cmd': user_cmd,
            'push': push_pack,
            'cmd_ord': token,
            'bat': battery,
            'charge': charge,
            'reason': loc_reason,
            'svr_ts': svr_ts,
            'dev_state':dev_state,
            'steps':steps,
            'cur_move_state':cur_move_state,
            'loc': {
                'gps': gps_dict,
                'wifi': wifi_list,
                'base': bs_list,
            },
            'fix_bs_loc': fix_bs_loc
        }, use_bin_type=True)
