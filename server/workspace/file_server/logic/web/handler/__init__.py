#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-28

@author: Jay
"""
import ujson
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from util.filetoken import gen_lvl_fn, gen_ref
from util.internal_forward.leveldb_encode import resolve_expire
from util.lib_common.file_ul import ul_args_ok, bi_directional_dispatch
from util.convert import bs2utf8
from util.internal_forward.leveldb_encode import encode as level_encode
from util.lib_common.file_down import cat_files
from common import down_parse
from config import LevelDBRpcClient, GCalcRdsInts, GMQDispRdsInts


SELECTED_SOURCES = ('0', '16')


@route(r'/down')
class ReadHandler(HttpRpcHandler):
    @web_adaptor(use_json_dumps=False)
    def get(self, tk, r):
        logger.debug('file down tk=%r, ref=%r' % (tk, r))
        resp = None

        #尝试多个src，兼容旧参数
        for src in SELECTED_SOURCES:
            _ = down_parse(tk, r, src)
            if not _:
                continue

            logger.debug(u'_ = %r', *_)
            resp = LevelDBRpcClient.forward(level_encode('snapshot', *_))
            if resp:
                break

        if not resp:
            self.send_error(400)
            return

        logger.debug(u'file down len(resp) = %r', len(resp))
        self.set_header('Content-Type', 'application/octet-stream')
        return resp


@route(r'/up')
class WriteHandler(HttpRpcHandler):
    @web_adaptor()
    def post(self, tk='0', src='0', usage='0'):
        """
        文件上传
        :param tk:
        :param src:
        :param usage:
        :return:
        """
        args = ul_args_ok(GCalcRdsInts, tk, src, usage)
        logger.debug(u'up args {0}'.format(args))
        if not args:
            self.send_error(400)
            return

        tk_params, file_source, usage, unique_sn = args
        logger.debug(u'up tk_params:{0},file_source:{1},usage:{2},unique_sn:{3}'.format(tk_params, file_source, usage, unique_sn))
        leveldb_fn = gen_lvl_fn(*tk_params)
        logger.debug(u'leveldb_fn {0}'.format(leveldb_fn))
        by = bs2utf8(self.get_argument('by', ''))
        expire = resolve_expire(file_source)
        logger.debug(u'lvl fn = %r, expire = %r', leveldb_fn, expire)

        #使用新的fn参数，存储文件
        LevelDBRpcClient.forward(level_encode('put', expire, leveldb_fn, self.request.body))

        bi_directional_dispatch(GMQDispRdsInts, unique_sn, tk_params, file_source, usage, leveldb_fn, by)
        self.finish(ujson.dumps({
            'r': gen_ref(*tk_params),
            'bi_token': unique_sn,
        }))


@route(r'/down_multi')
class MultiDownHandler(HttpRpcHandler):
    @web_adaptor(use_json_dumps=False)
    def get(self, params):
        params = (x.split(',') for x in params.split('|'))
        params = (x for x in params if 3 == len(x))

        d = {}
        for x in params:
            tk, ref, file_source = x
            _ = down_parse(tk, ref, file_source)
            if not _:
                continue
            resp = LevelDBRpcClient.forward(level_encode('snapshot', *_))
            if not resp:
                continue
            d.update({ref: resp})

        self.set_header('Content-Type', 'application/octet-stream')
        self.finish(cat_files(d))
