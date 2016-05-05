#coding:utf-8

import msgpack


def encode_skip(act, entity_id, rec_id, body=None):
    """
    :param entity_id: 实体id，例如设备id号，可多个用户共享
    :param rec_id: 记录id，例如监控记录行id
    :param body: 该记录对应的实体对象，json类型
    """
    assert act and isinstance(act, str)
    assert entity_id and isinstance(entity_id, str)
    assert rec_id and isinstance(rec_id, (int, long))

    p = {
        'act': act,
        'eid': entity_id,
        'rid': rec_id,
    }
    if body is not None:
        assert isinstance(body, dict)
        p.update({'p': body})

    return msgpack.packb(p, use_bin_type=True)