#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/7

@author: Jay
"""
from util.redis.redis_client import Redis
from setting import ACC_RDS_URI, DEV_RDS_URI


GAccRdsInts = Redis(ACC_RDS_URI)
GDevRdsInts = Redis(DEV_RDS_URI)