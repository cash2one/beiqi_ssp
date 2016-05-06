#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-29

@author: Jay
"""
import re

FEEDBACK_PATTERN = re.compile('^(?P<user_cmd>[_a-z]+):(?P<token>[a-f\d]+),(?P<state>[012])$')
REPORT_KEYS = ('user_cmd', 'token', 'state')

errno_map = {
    '0': 'fb_done',
    '1': 'fb_wait',
    '2': 'fb_busy',
}