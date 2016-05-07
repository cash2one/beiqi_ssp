#coding:utf-8
import plyvel
from util.convert import redis_encode_str, redis_encode_int, redis_encode_batch
from datetime import datetime, timedelta
from os import path


lvl_db_map = {}
ONEDAY_Delta = timedelta(seconds=86400)


def get(db, key, value=None):
    return redis_encode_str(db.get(key))


def snapshot(db, key, vlaue=None):
    with db.snapshot() as sn:
        return redis_encode_str(sn.get(key))


def put(db, key, value):
    db.put(key, value)
    return redis_encode_int(1)


def delete(db, key, value=None):
    db.delete(key)
    return redis_encode_int(1)


def _root_date(d):
    return '_'.join(('~/leveldb', d.strftime('%Y%m%d')))


def _clear_yesterday(now):
    global lvl_db_map

    yes_root = path.expanduser(_root_date(now - ONEDAY_Delta))
    yes_db = lvl_db_map.pop(yes_root, None)
    if yes_db:
        yes_db.close()
        plyvel.destroy_db(yes_root)


def resolve(cmd, expire, fn, value=None):
    """
    过期策略：暂时不计较expire的具体值，统一按1天处理
    """
    global lvl_db_map

    now = datetime.now()
    _clear_yesterday(now)

    func = globals().get(cmd)
    if not func:
        #只支持get/put/snapshot
        return redis_encode_batch()

    cur_root = path.expanduser('~/leveldb_files' if 0 == expire else _root_date(now))
    if cur_root not in lvl_db_map:
        lvl_db_map.update({cur_root: plyvel.DB(cur_root, create_if_missing=True)})

    return func(lvl_db_map.get(cur_root), fn, value)
