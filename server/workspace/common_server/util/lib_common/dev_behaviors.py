#coding:utf-8


from util.id_conv import parse_io_options, rawid_tuple


def sms_support(pid):
    """
    短信支持情况
    :param pid: 设备id
    0: 不能发短信
    1: 非结构化短信
    2: 结构化短信
    """
    _ = rawid_tuple(pid, True)
    if _ is None:
        return None
    pid, dev_type, dev_sn, io = _
    _, sms, _ = parse_io_options(io)
    if not sms:
        return 0
    if (dev_sn >> 22) & 0b1:
        #结构化短信
        return 2
    return 1


def wl_support(dev_type, dev_sn):
    """
    白名单支持情况
    :param dev_type: 设备类型
    :param dev_sn: 设备序号

    None: 没有白名单
    0: 不支持白名单
    1: 没有map字段
    2: 有map字段
    :return:
    """
    if dev_type not in (2, 7, 8):
        return 0
    if 7 == dev_type:
        #国内安徽电信
        return 1
    v2 = (dev_sn >> 22) & 0b1
    if 2 == dev_type:
        return 2 if v2 else 0
    #越南、意大利版本
    return 2 if v2 else 1