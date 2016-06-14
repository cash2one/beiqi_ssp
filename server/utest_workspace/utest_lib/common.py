#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-21

@author: Jay
"""
from gevent import monkey
monkey.patch_all()

import site
import os
import ujson
import random
import time
import unittest
import uuid
import urllib
import platform
import sys
import gevent
from gevent import threading

# remove unused utruner args
if len(sys.argv) >= 3:
    if "utrunner.py" in sys.argv[0]:
        sys.argv = sys.argv[1:-1]

from utils import error_code, logger, crypto
logger.init_log("unittest", "unittest")

from utils.network.tcp import TcpRpcClient, TcpRpcServer,  TcpRpcHandler
from utils.network.http import HttpRpcServer, HttpRpcHandler, HttpRpcClient
from utils.network.udp import UdpServer, UdpClient
from utils.wapper.web import web_adaptor
from utils.route import Route, route
from utils.meta.singleton import Singleton
from utils.data.cache import redis_client
from utils.crypto.sign import sign, checksign, Signer
from utils.service_control import setting as service_control_setting
from utils.service_control.cacher import ServiceMgrCacher, ParamCacher
from utils.service_control.setting import RT_HASH_RING, RT_CPU_USAGE_RDM
from utils.setting import enum


from utest_lib.common_fun import random_str
from common_fun import unittest_adaptor

from pandora.setting import SERVICE_TYPE as ST_PANDORA
from service_mgr.setting import SERVICE_TYPE as ST_SERVICE_MGR
from utest_umain.setting import *

SERVICE_TYPE = [
    ST_PANDORA,
]

