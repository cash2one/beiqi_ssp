#coding:utf-8


from tornado.web import RequestHandler
from utils import logger
from util.convert import bs2utf8
from util.torn_resp import json
from util.oem_conv import map_account_mobile_oem_key
from util.sso.account import *
from active_ensure import validate
from oem.compat_shanxi import map_shanxi_old_apikey
from mq_packs.uni_pack import shortcut_mq
from mq_packs.mysql_pack import pack as mysql_pack



class ActiveRegCodeHandler(RequestHandler):
    """
    凌拓帐号注册激活验证
    """
    def post(self):
        _ = validate(*(bs2utf8(self.get_argument(k)) for k in ('k', 'a', 'h', 'v')))
        if isinstance(_, int):
            self.finish(json.dumps({'state': _}))
            return

        is_oem, api_key, account, code, pwd = _
        api_key = map_shanxi_old_apikey(api_key)
        #仅仅凌拓本身和某些oem需要，因此mobile等价account
        mobile = account.split('@')[0]
        val_code = _account_cache.send_cmd(*get_newacc_reg_val(mobile))
        if not val_code:
            logger.warn('no redis entry for {0}'.format(mobile))
            self.finish(json.dumps({'state': 2}))
            return

        val_code, expect_api_key = val_code.split(':')
        if val_code != code:
            logger.warn('code not match')
            self.finish(json.dumps({'state': 2}))
            return

        if not expect_api_key:
            if api_key not in beiqi_keys:
                logger.warn('expect key empty, key not lt: {0}'.format(api_key))
                self.finish(json.dumps({'state': 5}))
                return
        else:
            if expect_api_key != api_key:
                logger.warn('api_key not match: {0} != {1}'.format(expect_api_key, api_key))
                self.finish(json.dumps({'state': 5}))
                return

        pwd_mask = cipher_pwd(pwd)
        cmds = combine_redis_cmds(set_account_pwd(account, pwd_mask))
        if is_oem:
            cmds = combine_redis_cmds(cmds, map_account_mobile_oem_key(api_key, account, mobile))
        _account_cache.send_multi_cmd(*cmds)

        mq_hub.send_cmd(
            *shortcut_mq(
                'gen_mysql',
                mysql_pack(
                    'sso_account',
                    {
                        'email': account,
                        'password': pwd_mask,
                        'cellphone': mobile,
                        'api_key': api_key,
                    },
                    0
                )
            )
        )

        self.finish(json.dumps({'state': 0}))
