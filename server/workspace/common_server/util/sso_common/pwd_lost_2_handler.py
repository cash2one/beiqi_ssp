#coding:utf-8

from tornado.web import RequestHandler

from util.convert import bs2utf8, combine_redis_cmds
from pwd_ensure import lost_parse
from util.torn_resp import json
from util.sso.account import get_pwd, get_mb_key, cipher_pwd, set_account_pwd, get_mobile, gen_lostpwd_val
from util.oem_conv import fix_account_postfix
from util.log_util import gen_log
from mq_packs.uni_pack import shortcut_mq
from mq_packs.normal_sms_pack import pack as sms_notify_pack
import random


def lost_stepbystep(api_key, auth_cipher, sign, ver=1):
    """
    一步一步确认
    :param api_key:
    :param auth_cipher:
    :param sign:
    :param ver:
    :return:
    """
    _ = lost_parse(api_key, auth_cipher, sign, ver)
    if isinstance(_, int):
        return {'state': _}

    typ, account, old_pwd, new_pwd, is_oem = _
    account = fix_account_postfix(account)
    redis_old_pwd, mb_apikey = _account_cache.send_multi_cmd(
        *combine_redis_cmds(
            get_pwd(account),
            get_mb_key(account)
        )
    )

    if not redis_old_pwd:
        #帐号不存在
        gen_log.warn('{0} not exist'.format(account))
        return {'state': 3}

    if is_oem and not mb_apikey:
        gen_log.warn('oem {0}, {1} not exist'.format(account, api_key))
        return {'state': 3}

    if mb_apikey:
        _, redis_api_key = mb_apikey.split(':')
        if redis_api_key != api_key:
            gen_log.warn('api_key not match: {0}, {1}'.format(redis_api_key, api_key))
            return {'state': 3}

    redis_mb = get_mobile(_account_cache, api_key, account)
    if 2 == typ:
        #短信验证
        val = ''.join((str(random.randint(0, 9)) for _ in xrange(6)))
        _account_cache.send_multi_cmd(*combine_redis_cmds(gen_lostpwd_val(account, val)))
        mq_hub.send_cmd(
            *shortcut_mq(
                'sms_notify',
                sms_notify_pack(redis_mb, 2, account, redis_mb, val)
            )
        )
        return {'state': 2}

    if redis_old_pwd != cipher_pwd(old_pwd):
        gen_log.debug('old pwd not match')
        return {'state': 4}
    if len(new_pwd) < 6:
        return {'state': 5}

    _account_cache.send_cmd(*set_account_pwd(account, cipher_pwd(new_pwd), False))
    return {'state': 0}


class PwdLost2Handler(RequestHandler):
    def post(self):
        self.finish(
            json.dumps(
                lost_stepbystep(*(bs2utf8(self.get_argument(k)) for k in ('k', 'a', 'h', 'v')))
            )
        )