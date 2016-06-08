#coding:utf-8
from tornado.web import RequestHandler
from tornado.gen import coroutine
from util.convert import bs2utf8
from util.internal_forward.leveldb_encode import encode as level_encode
from common import down_parse
from lib_common.file_down import cat_files
from config import GLevelDBClient


class MultiDownHandler(RequestHandler):
    @coroutine
    def get(self):
        params = bs2utf8(self.get_argument('params'))
        params = (x.split(',') for x in params.split('|'))
        params = (x for x in params if 3 == len(x))

        d = {}
        for x in params:
            tk, ref, file_source = x
            _ = down_parse(tk, ref, file_source)
            if not _:
                continue
            resp = yield GLevelDBClient.forward(level_encode('snapshot', *_))
            if not resp:
                continue
            d.update({ref: resp})

        self.set_header('Content-Type', 'application/octet-stream')
        self.finish(cat_files(d))
