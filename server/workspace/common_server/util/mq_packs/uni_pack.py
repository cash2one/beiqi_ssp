#coding:utf-8


import msgpack
from random import randint


def __pack(channel, biz_pack_dumps):
    """
    :param channel: 队列频道
    :param biz_pack_dumps: 业务队列打包结果
    """
    if not (channel and isinstance(channel, str)):
        raise ValueError('uni_pack channel not str: {0}'.format(channel))
    if not (biz_pack_dumps and isinstance(biz_pack_dumps, str)):
        raise ValueError('biz_pack_dumps not str: {0}'.format(biz_pack_dumps))

    return msgpack.packb(
        {
            'c': channel,
            'p': biz_pack_dumps,
        }, use_bin_type=True)


def shortcut_mq(watch_ch, biz_pack_dumps):
    return 'rpush', str(randint(1, 10)), __pack(watch_ch, biz_pack_dumps)