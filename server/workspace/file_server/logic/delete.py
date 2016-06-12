#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/12

@author: Jay
"""
from tornado.web import RequestHandler
from tornado.gen import coroutine
from util.convert import bs2utf8
from util.internal_forward.leveldb_encode import encode as level_encode
from config import  GLevelDBClient
SELECTED_SOURCES = ('0', '16')


class DeleteFileHandler(RequestHandler):
    @coroutine
    def get(self):
        """
        文件上传
        """
        file = bs2utf8(self.get_argument("file"))
        if not file:
            self.send_error(400)
            return

        #使用新的fn参数，存储文件
        yield GLevelDBClient.forward(level_encode('delete', 0, file))
        self.finish({"status":0})