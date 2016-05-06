#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/3

@author: Jay
"""
from util.redis.redis_client import Redis
from utils.network.tcp import LevelDBRpcClient
from setting import CALC_RDS_URI, MQ_DISP_RDS_URI, LEVEL_DB_HOST


GCalcRdsInts = Redis(CALC_RDS_URI)
GMQDispRdsInts = Redis(MQ_DISP_RDS_URI)

GLevelDBClient = LevelDBRpcClient(*LEVEL_DB_HOST.split(":"))
