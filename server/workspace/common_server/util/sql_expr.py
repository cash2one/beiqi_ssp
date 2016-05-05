#coding:utf-8


from datetime import datetime
from torndb import Connection
from utils import logger


def _insert_one(tab_name, one):
    percent_s = ''.join(('(', ', '.join(('%s', ) * len(one)), ')'))
    key_order = one.keys()
    for k, v in one.iteritems():
        if not isinstance(v, (str, int, long, float, bool, datetime)):
            logger.debug('unsupported sql type: %r, %r, %r in %r' % (k, v, type(v), tab_name))
            raise ValueError('unsupported sql type: {0}, {1}, {2} in {3}'.format(k, v, type(v), tab_name))

    return 'insert into {0} ({1}) values {2}'.format(
        tab_name,
        ', '.join(('`{0}`'.format(x) for x in key_order)),
        percent_s), key_order


def _insert(torndb, tab_name, ob):
    sql, ko = _insert_one(tab_name, ob if isinstance(ob, dict) else ob[0])
    if isinstance(ob, dict):
        return torndb.insert(sql, *(ob.get(k) for k in ko))
    return torndb.insertmany(sql, [[x.get(k) for k in ko] for x in ob])


def _delete(torndb, tab_name, del_kvs):
    """
    删除记录
    :param torndb:
    :param tab_name:
    :param del_kvs: 待删除的索引字段
    """
    assert del_kvs and isinstance(del_kvs, dict)
    where = ' and '.join(('`{0}` = %s'.format(k) for k in del_kvs.iterkeys()))
    return torndb.execute('delete from {0} where {1} '.format(tab_name, where), *del_kvs.values())


def _set_update(ob):
    for k, v in ob.iteritems():
        if not isinstance(v, (str, int, long, float, bool, datetime)):
            raise ValueError('unsupported sql type: {0}, {1}, {2}'.format(k, v, type(v)))

        if isinstance(v, str):
            v = "'{0}'".format(v)
        elif isinstance(v, datetime):
            v = "'{0}'".format(v.strftime('%Y-%m-%d %H:%M:%S'))
        elif isinstance(v, bool):
            v = '{0}'.format(int(v))
        yield '`{0}` = {1}'.format(k, v)


def _update(torndb, tab_name, ob, update_kvs):
    if not (update_kvs and isinstance(update_kvs, dict)):
        raise ValueError('update_kv invalid: {0}'.format(update_kvs))
    if not (ob and isinstance(ob, dict)):
        raise ValueError('update ob invalid: {0}'.format(ob))

    where = ' and '.join(('`{0}` = %s'.format(k) for k in update_kvs.iterkeys()))
    return torndb.update(
        'update {0} set {1} where {2}'.format(
            tab_name,
            ', '.join(_set_update(ob)),
            where),
        *update_kvs.values()
    )


def _tr_time_fields(x, *time_fields):
    """
    翻译时间字段
    :param x: dict对象
    :param time_fields: 时间字段表
    :return:
    """
    if not (x and isinstance(x, dict)):
        return
    for f in time_fields:
        v = x.get(f)
        if v and isinstance(v, int):
            x[f] = datetime.fromtimestamp(v)
        elif v and isinstance(v, str):
            x[f] = datetime.strptime(v, '%Y-%m-%d %H:%M:%S')


def exec_sql(torndb, tab_name, ob, act, ref_kwargs=None, *time_fields):
    """
    :param ref_kwargs: 更新/删除 依赖键值

    v2版更新说明：
    1. 支持insertmany操作（update不需要）
    2. 原始接口保持不变，通过ob参数类型判定是否为many；many操作要求ob对象结构一致
    """
    if not (tab_name and isinstance(tab_name, str)):
        raise ValueError('tab_name invalid: {0}'.format(tab_name))
    if not (torndb and isinstance(torndb, Connection)):
        raise ValueError('torndb invalid: {0}'.format(torndb))
    if not isinstance(act, int) and act in (0, 1, 2):
        raise ValueError('unknown action: {0}'.format(act))
    if ob:
        if not isinstance(ob, (dict, list, tuple)):
            raise ValueError('ob invalid: {0}'.format(ob))

    if isinstance(ob, dict):
        _tr_time_fields(ob, *time_fields)
    elif isinstance(ob, (list, tuple)):
        [_tr_time_fields(x, *time_fields) for x in ob]

    if 0 == act:
        return _insert(torndb, tab_name, ob)
    #delete
    if 1 == act:
        return _delete(torndb, tab_name, ref_kwargs)
    return _update(torndb, tab_name, ob, ref_kwargs)
