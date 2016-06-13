#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/13

@author: Jay
"""
from util.redis.redis_client import Redis
from setting import DEV_RDS_URI


GDevRdsInts = Redis(DEV_RDS_URI)