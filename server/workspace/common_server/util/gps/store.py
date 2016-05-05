#coding:utf8

import numbers
from cal import cal_aprx, conv_raw
from util.log_util import gen_log
from util.convert import redis_encode_batch


_aprx_fmt = 'aprx:{0}:{1}'


def resolve_gps_table(typ, sn):
    """
    以1000为单位分表
    :param sn: 设备id序号
    :param typ: 设备类型
    """
    index = sn / 1000
    return '_'.join(('gps', str(typ), str(index)))


def save_memcache(pid, lg, la, ts, from_, radius, addr, token, cmd, battery=0):
    gen_log.debug('mc gps: {0}, {1}, {2}, {3}, {4}'.format(pid, lg, la, ts, from_))
    if lg is None:
        return
    if not isinstance(lg, numbers.Real) and not isinstance(la, numbers.Real):
        return
    if not isinstance(ts, int):
        gen_log.warn('ts invalid: {0}'.format(ts))
        return
    if not isinstance(from_, int):
        gen_log.warn('from_ invalid: {0}'.format(from_))
        return
    if not isinstance(radius, int):
        gen_log.warn('radius invalid: {0}'.format(radius))
        return
    if not (isinstance(addr, str) and isinstance(token, (int, long)) and isinstance(cmd, str)):
        gen_log.warn('args invalid: {0}, {1}'.format(token, cmd))
        return

    lg = conv_raw(lg)
    la = conv_raw(la)

    return ':'.join(('gps_loc', pid)), redis_encode_batch(lg, la, ts, from_, radius, battery, token, cmd, addr)


def _aprx(lgti, lati, ratio, level):
    def __(t):
        return tuple((float(cal_aprx(x, ratio)) for x in t))

    lgti = float(cal_aprx(lgti, ratio))
    lati = float(cal_aprx(lati, ratio))

    yield __((lgti, lati))

    for i in xrange(1, level):
        seed = i * 1.0 / (10 ** ratio)

        yield __((lgti + seed, lati))
        yield __((lgti - seed, lati))
        yield __((lgti, lati + seed))
        yield __((lgti, lati - seed))
        yield __((lgti + seed, lati + seed))
        yield __((lgti + seed, lati - seed))
        yield __((lgti - seed, lati + seed))
        yield __((lgti - seed, lati - seed))


def resolve_around(lg, la, ratio=2, level=2):
    """查找附近
    考虑到redis异步查询，故将redis的调用放至上层执行
    且计算距离也在上层执行，仅返回hget的键值
    redis:HGET
    aprx:121.43:31.22
    :param lg: 东经
    :param la: 北纬
    :param ratio: 小数点精度
    :param level: 近似值精度左右偏移的层次
    """
    assert isinstance(lg, numbers.Real)
    assert isinstance(la, numbers.Real)

    lg = conv_raw(lg)
    la = conv_raw(la)
    return (_aprx_fmt.format(*x) for x in _aprx(lg, la, ratio, level))


def latest_loc(id_):
    """最近一次的位置
    同样仅返回相关键值，不做实际redis调用
    :param id_: 设备id
    """
    assert id_ and isinstance(id_, str) and 8 == len(id_)
    return 'exist', id_