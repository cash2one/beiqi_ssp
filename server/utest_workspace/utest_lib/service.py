#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-6-4

@author: Jay
"""
from utils.service_control.cacher import ServiceMgrCacher
from lib.common import ST_PANDORA
from utils.service_control.setting import PT_HTTP


# pandora
PandoraHttpClt = ServiceMgrCacher().get_connection(ST_PANDORA, protocol=PT_HTTP)