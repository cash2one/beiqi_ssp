#coding:utf-8

from tornado.web import RequestHandler

from util.convert import bs2utf8, combine_redis_cmds
from pwd_ensure import new_parse
from util.torn_resp import json
from util.sso.account import cipher_pwd, set_account_pwd
from util.sso.account import review_lostpwd_val, pass_lostpwd_val
from util.log_util import gen_log
from util.oem_conv import fix_account_postfix


def new_check(api_key, auth_cipher, sign, ver=1):
    _ = new_parse(api_key, auth_cipher, sign, ver)
    if isinstance(_, int):
        return {'state': _}

    account, x_val, new_pwd = _
    if not (account and x_val and new_pwd):
        gen_log.warn('arg missing')
        return {'state': 3}

    account = fix_account_postfix(account)
    review_val = _account_cache.send_multi_cmd(*combine_redis_cmds(review_lostpwd_val(account)))
    if not review_val:
        gen_log.warn('no val for new_pwd: {0}'.format(account))
        return {'state': 3}

    if x_val != review_val:
        gen_log.warn('val notmatch')
        return {'state': 4}

    _account_cache.send_multi_cmd(
        *combine_redis_cmds(
            pass_lostpwd_val(account),
            set_account_pwd(account, cipher_pwd(new_pwd), False)
        )
    )
    return {'state': 0}


class PwdNew2Handler(RequestHandler):
    def post(self):
        self.finish(
            json.dumps(
                new_check(*(bs2utf8(self.get_argument(k)) for k in ('k', 'a', 'h', 'v')))
            )
        )