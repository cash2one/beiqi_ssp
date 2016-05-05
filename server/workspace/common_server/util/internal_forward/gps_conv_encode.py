#coding:utf-8


from util.convert import redis_encode_batch
from . import prepend_head


@prepend_head
def earth2mars(lat, log):
    """
    地球转火星
    :param lat: 北纬
    :param log: 东经
    """
    return redis_encode_batch('earth2mars', lat, log)


@prepend_head
def cdma_bs_fix(bs_lat, bs_log, an_lat, an_log):
    """
    cdma基站修正
    :param bs_lat:
    :param bs_log:
    :param an_lat:
    :param an_log:
    :return:
    """
    return redis_encode_batch('cdma_bs_fix', bs_lat, bs_log, an_lat, an_log)