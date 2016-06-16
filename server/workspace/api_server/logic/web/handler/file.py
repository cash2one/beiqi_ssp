#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/4

@author: Jay
"""
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from util.lib_common.file_ul import common_file_token
from utils.crypto.beiqi_sign import client_sign_wapper
from config import GDevRdsInts, GAccRdsInts


@route(r'/res/file_tk', name='/res/file_tk')
class FileTokenHandler(HttpRpcHandler):
    """
    账号token
    """
    @web_adaptor()
    @client_sign_wapper(GAccRdsInts)
    def get(self, username, fn, m, r='', *args, **kwargs):
        resp = common_file_token(
            GDevRdsInts,
            username,
            fn,
            m,
            r
        )

        logger.debug('file tk resp={0}'.format(resp))

        if not resp:
            self.set_status(400)
            return

        return resp


def _single(account, x):
    fn, mode, ref = x
    return ref, common_file_token(GDevRdsInts, account, fn, mode, ref)


@route(r'/res/filetk_multi', name='/res/filetk_multi')
class MultiFileTokenHandler(HttpRpcHandler):
    @web_adaptor()
    @client_sign_wapper(GAccRdsInts)
    def get(self, user_name, params, *args, **kwargs):
        params = params.split('|')
        params = (x.split(',') for x in params)
        params = (x for x in params if 3 == len(x))

        return dict((_single(user_name, x) for x in params))


