#coding:utf-8
from tornado.web import RequestHandler
from tornado.gen import coroutine
from util.convert import bs2utf8
from util.internal_forward.leveldb_encode import encode as level_encode
from common import down_parse
from utils import logger
from config import GLevelDBClient

SELECTED_SOURCES = ('0', '16')


class ReadHandler(RequestHandler):
    @coroutine
    def get(self):
        tk = bs2utf8(self.get_argument('tk'))
        ref = bs2utf8(self.get_argument('r'))

        logger.debug('file down tk=%r, ref=%r' % (tk, ref))
        resp = None

        #尝试多个src，兼容旧参数
        for src in SELECTED_SOURCES:
            _ = down_parse(tk, ref, src)
            if not _:
                continue

            logger.debug(u'_ = %r', *_)
            resp = yield GLevelDBClient.forward(level_encode('snapshot', *_))
            if resp:
                break

        if not resp:
            self.send_error(400)
            return
        logger.debug(u'file down len(resp) = %r', len(resp))
        self.set_header('Content-Type', 'application/octet-stream')
        self.finish(resp)
