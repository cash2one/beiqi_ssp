#coding:utf-8


import msgpack


def pack(tn, ob):
    """
    :param tn: 集合名
    :param ob: 对象
    """
    assert tn and isinstance(tn, str)
    assert ob and isinstance(ob, dict)

    return msgpack.packb({
        '_tn': tn,
        'ob': ob
    }, use_bin_type=True)