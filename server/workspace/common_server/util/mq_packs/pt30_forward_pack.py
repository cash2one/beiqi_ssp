# coding:utf-8


import msgpack


def pack(cb, ptu_id, p):
    """
    pt30转发打包

    :param cb: 编码函数
    :param ptu_id: 设备id
    :param p: payload
    """
    if not (cb and isinstance(cb, str)):
        raise ValueError('cb not str: %s' % type(cb))
    if not (ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)):
        raise ValueError('pid not str: %s' % type(ptu_id))

    return msgpack.packb(
        {
            'cb': cb,
            'pid': ptu_id,
            'p': p
        },
        use_bin_type=True
    )