#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-17

@author: Jay
"""
import os
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from lib import gaode_loc


@route(r'/location')
class LocationHandler(HttpRpcHandler):
    @web_adaptor(use_json_dumps=False)
    def get(self, *args, **kwargs):
        # 高德定位
        loc_result = gaode_loc(**kwargs)
        return loc_result
