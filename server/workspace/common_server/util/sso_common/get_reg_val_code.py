# coding:utf-8

from tornado.web import RequestHandler
from util.sso.account import get_newacc_reg_val
from util.convert import bs2utf8
from util.log_util import gen_log
import json


class GetRegValCodeHandler(RequestHandler):
    def get(self):
        mobile = bs2utf8(self.get_argument('mobile'))

        val_code = _account_cache.send_cmd(*get_newacc_reg_val(mobile))
        gen_log.debug('get reg val code, val_code: {0}'.format(val_code))

        val_code = val_code.split(':')[0]

        if not val_code:
            self.send_error(400)
            return

        self.finish(json.dumps({'val_code': int(val_code)}))
