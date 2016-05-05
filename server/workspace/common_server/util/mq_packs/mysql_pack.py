#coding:utf-8


import msgpack


def mysql_rewind(mq_ch_name, mq_payload):
    """
    mysql执行完成后执行队列回调
    :param mq_ch_name: 队列频道名，参考uni_mq设计
    :param mq_payload: 队列payload
    """
    if not (mq_ch_name and isinstance(mq_ch_name, str)):
        raise ValueError('mq channel invalid: {0}'.format(mq_ch_name))
    if not (mq_payload and isinstance(mq_payload, str)):
        raise ValueError('mq_payload not str: {0}'.format(mq_payload))

    return {
        '_non_mysql': {
            'mqc': mq_ch_name,
            'mqp': mq_payload
        }
    }


def mysql_foreign(fk, table_name, payload, fk_group=None):
    """
    外键写入
    :param fk: 外键名
    :param table_name: 关联表名
    :param payload:
    :param fk_group: 外键组
    :return:
    """
    key = '_'.join(('_mysql', fk_group or ''))
    return {key: (table_name, fk, payload)}


def pack(table_name, payload, action=0, ref_kvs=None, *time_fields, **kwargs):
    """
    :param action: 0：插入，1：删除，2：更新
    :param ref_kvs: 用于删除或更新
    :param time_fields: 时间格式字段
    :param kwargs: 用于执行后回调
    """
    if not (table_name and isinstance(table_name, str)):
        raise ValueError('table_name not str: %s' % table_name)
    if action not in (0, 1, 2):
        raise ValueError('unknown action: %s' % action)
    if 0 == action:
        #添加必须为dict或list/tuple
        if not (payload and isinstance(payload, (dict, tuple, list))):
            raise ValueError('insert payload invalid: {0}'.format(payload))
    if 2 == action:
        if not (payload and isinstance(payload, dict)):
            raise ValueError('update payload invalid: {0}'.format(payload))
    if ref_kvs:
        if not isinstance(ref_kvs, dict):
            raise ValueError('ref_kvs not dict: %s' % type(ref_kvs))

    d = {
        'tn': table_name,
        'pld': payload,
        'act': action,
        'key': ref_kvs,
        'tsf': time_fields
    }
    d.update(**kwargs)
    return msgpack.packb(d, use_bin_type=True)
