#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/6

@author: Jay
"""
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor


@route(r'/wechat/pages/comment')
class CommentHandler(HttpRpcHandler):
    @web_adaptor(use_http_render=False)
    def get(self, text, *args, **kwargs):
        self.render('wechat_comment.html', text=text)