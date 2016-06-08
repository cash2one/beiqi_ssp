#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/3

@author: Jay
"""
from util.redis.redis_client import Redis
from util.internal_forward.gen_internal_client import GeneralInternalClient
from setting import CALC_RDS_URI, MQ_DISP_RDS_URI, LEVEL_DB_HOST
from util.convert import parse_ip_port


GCalcRdsInts = Redis(CALC_RDS_URI)
GMQDispRdsInts = Redis(MQ_DISP_RDS_URI)
GLevelDBClient = GeneralInternalClient(parse_ip_port(LEVEL_DB_HOST))


