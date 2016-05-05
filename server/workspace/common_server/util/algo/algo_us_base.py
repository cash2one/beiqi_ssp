#coding:utf-8


from common import *


def convert(days, in_ts, out_ts, safe_level, bsid, nid, sid, rssi):
    """
    算法基站转换
    """
    d = {
        'days': algodays_us(days),
        'in_ts': algo_inoutts_us(in_ts),
        'out_ts': algo_inoutts_us(out_ts),
    }

    if any((not is_num(x) for x in (bsid, nid, sid, rssi))):
        raise ValueError('bs invalid: bsid, nid, sid, rssi')

    d.update({
        'bsid': int(bsid),
        'nid': int(nid),
        'sid': int(sid),
        'rssi': conv_base_rssi(int(rssi))
    })

    if 3 == safe_level:
        d.update({'name': '学校'})
    if 6 == safe_level:
        d.update({'name': '家'})

    return d