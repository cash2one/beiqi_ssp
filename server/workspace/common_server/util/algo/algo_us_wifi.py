#coding:utf-8


from common import *


def convert(days, in_ts, out_ts, safe_level, *mac_rssi_tuple):
    """
    打包wifi安全区
    :param days: 有效天
    :param in_ts: 进入时间
    :param out_ts: 离开时间
    :param mac_rssi_tuple: mac地址与信号强度tuple, like ('ab:cd:ef:12:34:56', 28)
    """
    #至少一组mac地址和信号强度对
    if not len(mac_rssi_tuple) >= 1:
        raise ValueError('wifi mac atleast 1')
    if not isinstance(safe_level, int):
        raise ValueError('wifi safe_level not int, but %s' % type(safe_level))

    d = {
        'days': algodays_us(days),
        'in_ts': algo_inoutts_us(in_ts),
        'out_ts': algo_inoutts_us(out_ts),
    }

    if 3 == safe_level:
        d.update({'name': '学校'})
    if 6 == safe_level:
        d.update({'name': '家'})

    for i, t in enumerate(mac_rssi_tuple):
        d.update({
            'mac_{0}'.format(i): conv_mac(t[0]),
            'rssi_{0}'.format(i): conv_wifi_rssi(algo_wifi_rssi_us(t[1]))
        })

    return d