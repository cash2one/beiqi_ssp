#coding:utf-8

import msgpack
from util.oem_conv import OEM_KEY_PATTERN


class SmsType:
    REGISTER = 0
    FOLLOW_REQ = 1
    RESET_PWD = 2
    SOS_SMS = 3


def pack(dst_mobile, typ, dst_acc, *params, **kwargs):
    """
    编码短信，减少msgpack交换字节，仅仅打包参数
    虽然mq中能根据dst_acc查询手机号，但多了一次对redis的读操作

    注意：注册短信发送，由于mobile和api_key尚未建立关系
    按照现有代码会默认使用凌拓通道
    故加入api_key参数，除注册之外该参数不用传递

    基于云南移动的奇葩需求，参数一致性如下:
    dst_mobile为空时，mq默认替换为目标帐号

    :param dst_mobile: 手机号
    :param typ: 短信类型
    :param dst_acc: 目标帐号
    :param params: 短信参数列表
    """
    if not isinstance(typ, int):
        raise ValueError('typ invalid: %s' % type(typ))
    if not (dst_acc and isinstance(dst_acc, str)):
        raise ValueError('dst_acc invalid: {0}'.format(dst_acc))

    d = {
        'n': dst_mobile,
        't': typ,
        'a': dst_acc,
        'p': params
    }

    api_key = kwargs.get('api_key')
    if api_key and isinstance(api_key, str) and OEM_KEY_PATTERN.search(api_key):
        d.update({'k': api_key})

    return msgpack.packb(d, use_bin_type=True)