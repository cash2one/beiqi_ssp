#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-26

@author: Jay
"""
import re

TIME_STR_REGEX = re.compile("^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}$")
INT_REGEX = re.compile("^[1-9]\d*$")
IP_REGEX = re.compile("(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\."
                      "(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])")
PHONE_REGEX = re.compile("^1\d{10}$")
