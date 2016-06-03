#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/3

@author: Jay
"""
import urllib2
from utils import logger
from utils.network.http import HttpRpcClient
from utils.wapper.catch import except_adaptor
from setting import *


@except_adaptor(is_raise=False)
def gaode_loc(accesstype="", imei="",smac="", serverip="", cdms=0, imsi="", network="", tel="", bts="", nearbts="", mmac="",macs="",output="json"):
    """
    高德定位
    :param accesstype: 移动端接入网络方式，必填，默认无
                        可选值：
                            移动接入网络：0
                            wifi接入网络：1
    :param imei: 手机imei号 ，必填，默认无
                        此参数能够提高定位精度和准确度，且定位不到时可依据此参数进行跟踪排查，如没有则无法排查和跟踪问题
    :param smac: 手机mac码 ，非必填，但建议填写 ，默认无
                        此参数能够提高定位精度和准确度，且定位不到时可依据此参数进行跟踪排查，如没有则无法排查和跟踪问题
    :param serverip: 设备接入基站时对应的网关IP ，非必填，但建议填写 ，默认无
                        此参数能够提高定位精度和准确度，且定位不到时可依据此参数进行跟踪排查，如没有则无法排查和跟踪问题
    :param cdma: 是否为cdma ，accesstype=0时，必填 ，默认0，
                        是否为cdma
                        非cdma：0
                        是cdma：1
    :param imsi: 移动用户识别码 ，非必填，但建议填写 ，默认无
                        此参数能够提高定位精度和准确度，且定位不到时可依据此参数进行跟踪排查，如没有则无法排查和跟踪问题
    :param network: 无线网络类型 ，accesstype=0时，必填 ，默认无
                        GSM/GPRS/EDGE/HSUPA/HSDPA/WCDMA
    :param tel : 手机号码 ，非必填，accesstype=0时，必填 ，默认无
    :param bts : 接入基站信息，accesstype=0时，必填 ，默认无
                        非CDMA格式为：mcc,mnc,lac,cellid,signal
                        CDMA格式为：sid,nid,bid,lon,lat,signal，
                        其中lon,lat可为空，格式为：sid,nid,bid,,,signal
    :param nearbts: 周边基站信息（不含接入基站信息）， 非必填 ，默认无
                        基站信息1|基站信息2|基站信息3…
    :param mmac: 已连热点mac信息 ， 非必填，但强烈建议填写，默认无
                        mac,signal,ssid。 如：f0:7d:68:9e:7d:18,-41,TPLink
    :param macs : wifi列表中mac信息 ， accesstype=1时，必填 ，默认无
                        单mac信息同mmac，mac之间使用“|”分隔。必须填写2个及2个以上,30个以内的方可正常定位。请不要包含移动wifi信息
    :param output : 返回数据格式类型 ， 可选 ，默认：json
                        可选值：json,xml
    :return: 字符串格式
    """
    params = {
        "accesstype": accesstype,
        "imei": imei,
        "smac": smac,
        "serverip": serverip,
        "cdms": cdms,
        "imsi": imsi,
        "network": network,
        "tel": tel,
        "bts": bts,
        "nearbts": nearbts,
        "mmac": mmac,
        "macs": macs,
        "output": output,
        "key": GAODE_LOC_APP_KEY
    }

    FULL_URL = GAODE_LOC_URL + "?" + "&".join("%s=%s"%(k, urllib2.quote(v)) for k,v in params.items())
    logger.debug('gaode_loc, FULL_URL=%r' % FULL_URL)
    return HttpRpcClient().fetch_async(url=FULL_URL)
