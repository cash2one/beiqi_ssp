#coding:utf-8

import math


#地球半径
_EARTH_RADIUS = 6378137
pi = 3.14159265358979324


def conv_raw(v):
    """兼容度数和整数2种格式
    """
    v = float(v)
    if v <= 180:
        return v
    return v / 3600.0


def cal_aprx(x, aprx_ratio):
    """计算近似值
    @param x: 浮点数
    @param aprx_ratio: 精确度，默认精确小数点后2位
    """
    x = conv_raw(x)
    return '%0.{0}f'.format(aprx_ratio) % x


def _cal_ax(x):
    return x * math.pi * 1.0 / 180


def cal_dist(p1, p2):
    """计算两点间的距离
    返回单位为米

    @param p1: (经度，纬度）
    """
    assert p1 and isinstance(p1, (list, tuple)) and 2 == len(p1)
    assert p2 and isinstance(p2, (list, tuple)) and 2 == len(p2)

    x1, y1 = p1
    x2, y2 = p2

    x1 = _cal_ax(x1)
    y1 = _cal_ax(y1)

    x2 = _cal_ax(x2)
    y2 = _cal_ax(y2)

    dx = abs(x1 - x2)
    dy = abs(y1 - y2)

    p = math.pow(math.sin(dx / 2), 2) + math.cos(x1) * math.cos(x2) * math.pow(math.sin(dy / 2), 2)
    return _EARTH_RADIUS * 2 * math.asin(math.sqrt(p))


#print '%r' % cal_dist((121.420675, 31.224286666667), (121.42647022694, 31.220157068379))
