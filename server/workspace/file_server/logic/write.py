#coding:utf-8
from tornado.web import RequestHandler
from tornado.gen import coroutine
from util.convert import bs2utf8
from util.torn_resp import json
from util.filetoken import gen_lvl_fn, gen_ref
from util.internal_forward.leveldb_encode import encode as level_encode, resolve_expire
from utils import logger
from lib_common.file_ul import ul_args_ok, bi_directional_dispatch
from config import GMQDispRdsInts, GCalcRdsInts, GLevelDBClient


class WriteHandler(RequestHandler):
    @coroutine
    def post(self):
        """
        文件上传
        """
        args = ul_args_ok(GCalcRdsInts, *(bs2utf8(self.get_argument(k, '0')) for k in ('tk', 'src', 'usage')))
        logger.debug(u'up args {0}'.format(args))
        if not args:
            self.send_error(400)
            return

        tk_params, file_source, usage, unique_sn = args
        leveldb_fn = gen_lvl_fn(*tk_params)
        by = bs2utf8(self.get_argument('by', ''))
        expire = resolve_expire(file_source)
        logger.debug(u'lvl fn = %r, expire = %r', leveldb_fn, expire)

        #使用新的fn参数，存储文件
        yield GLevelDBClient.forward(level_encode('put', expire, leveldb_fn, self.request.body))

        bi_directional_dispatch(GMQDispRdsInts, unique_sn, tk_params, file_source, usage, leveldb_fn, by)
        self.finish(json.dumps({
            'r': gen_ref(*tk_params),
            'bi_token': unique_sn,
        }))
