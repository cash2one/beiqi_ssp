#coding:utf-8


def pack(pid, src_ts, token, battery, loc_reason, autonavi_dict, *wifis):
    """
    打包gen_gps任务处理完成后，转发其他任务模块

    :param pid: 设备id
    :param src_ts: 设备时间，非服务器时间
    :param token: 定位事件token
    :param battery: 电量
    :param loc_reason: 定位原因，例如低电量等
    :param autonavi_dict: 高德返回数据结构，如果是gps定位，需自己构造
    :return:
    """

    if not (pid and isinstance(pid, str) and 8 == len(pid)):
        raise ValueError('pid invalid: %s' % pid)
    if not (src_ts and isinstance(src_ts, int)):
        raise ValueError('src_ts not int: %s' % type(src_ts))
    if not (token and isinstance(token, int)):
        raise ValueError('token not int: %s' % type(token))
    if not isinstance(battery, int):
        raise ValueError('battery not int: %s' % type(battery))
    if not isinstance(loc_reason, int):
        raise ValueError('loc_reason not int: %s' % type(loc_reason))
    if not (autonavi_dict and isinstance(autonavi_dict, dict)):
        raise ValueError('autonavi_dict not dict: %s' % type(autonavi_dict))

    return {
        'pid': pid,
        'src_ts': src_ts,
        'token': token,
        'bat': battery,
        'reason': loc_reason,
        'ad': autonavi_dict,
        'wifi': wifis,
    }