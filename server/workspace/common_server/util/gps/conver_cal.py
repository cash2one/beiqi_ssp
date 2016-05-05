#coding:utf-8

from math import cos, sin, acos, radians

# 地球半径(单位：米）
RE = 6371004

def cal_dist(p1, p2):
    """
    参数为度表示的经纬度
    :param p1: 东经、北纬
    :param p2: 东经、北纬
    """
    # 转为弧度
    lon_p1 = radians(p1[0])
    lat_p1 = radians(p1[1])

    lon_p2 = radians(p2[0])
    lat_p2 = radians(p2[1])

    return RE * acos(sin(lat_p1) * sin(lat_p2) + cos(lat_p1) * cos(lat_p2) * cos(lon_p1 - lon_p2))