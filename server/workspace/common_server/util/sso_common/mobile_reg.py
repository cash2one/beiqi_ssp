#coding:utf-8


from util.convert import is_mobile, combine_redis_cmds
from util.sso.account import gen_newacc_reg_val
from utils import logger
from mq_packs.uni_pack import shortcut_mq
from mq_packs.normal_sms_pack import pack as sms_notify_pack, SmsType
from random import randint


def reg_via_mobile(account, api_key):
    """
    通过手机号注册
    :param account: 用户帐号
    :param api_key:
    :return:
    """
    mobile = account.split('@')[0]
    if not is_mobile(mobile):
        return

    val_code = ''.join((str(randint(0, 9)) for _ in xrange(6)))
    logger.debug('val_code %s sent' % val_code)
    #该接口需兼容oem，故填入空api_key
    _account_cache.send_multi_cmd(*combine_redis_cmds(gen_newacc_reg_val(mobile, val_code, api_key or '')))
    mq_hub.send_cmd(
       *shortcut_mq(
           'sms_notify',
           sms_notify_pack(
               mobile,
               SmsType.REGISTER,
               account,
               val_code,
               api_key=api_key
           )
       )
    )

    logger.debug('account %s val_code %s sent' % (account, val_code))

    return True
