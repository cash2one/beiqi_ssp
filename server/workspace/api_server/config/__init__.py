#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/3

@author: Jay
"""
from api_server.setting import ACC_RDS_URI, CALC_RDS_URI, DEV_RDS_URI, MQ_DISP_RDS_URI, LEVEL_DB_HOST
from util.convert import resolve_redis_url
from utils.data.cache.redis_client import RedisClient
from utils.network.tcp import LevelDBRpcClient

GAccRdsInts = RedisClient(*resolve_redis_url(ACC_RDS_URI)[:4])
GCalcRdsInts = RedisClient(*resolve_redis_url(CALC_RDS_URI)[:4])
GDevRdsInts = RedisClient(*resolve_redis_url(DEV_RDS_URI)[:4])
GMQDispRdsInts = RedisClient(*resolve_redis_url(MQ_DISP_RDS_URI)[:4])

GLevelDBClient = LevelDBRpcClient(*LEVEL_DB_HOST.split(":"))
