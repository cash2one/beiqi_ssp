#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/3

@author: Jay
"""
from utils.data.db.mysql_manual import SchemaTable
from utils.service_control.cacher import ParamCacher
from utils.service_control.parser import ArgumentParser
from setting import DB_NAME


DBBeiqiSspInst = SchemaTable.instance(ParamCacher().db_instance, ArgumentParser().args.db_name, DB_NAME)