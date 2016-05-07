#coding:utf-8
from utils import logger
from util.oem_account_key import oem_accounts, beiqi_keys
from util.stream_config_client import load as conf_load
from util.redis.redis_client import Redis
from util.oem_conv import get_mb_key
from util.lib_tr.tr import tr_txt, resolve_lang
from util.lib_tr.langs import sms_template
from vcomcn import vcomcn_sms


_account_cache = Redis(dict(conf_load('redis.ini')).get('redis.ini').get('oauth', 'url'))
default_arg = {0: '凌拓', 1: '邦邦熊', }


def sms_func(api_key):
    """
    获取调用短信方法
    :param api_key:
    """
    logger.debug('sms_func: {0}'.format(api_key))
    if not api_key or api_key in beiqi_keys:
        #没有akey
        return vcomcn_sms

    ob = oem_accounts.get(api_key)
    if not ob:
        #oem key不存在
        raise ValueError('sms_func: {0} not exist'.format(api_key))

    func = ob.get('f')
    if not func:
        logger.warn('no f field: {0}'.format(ob))
        return vcomcn_sms
    return globals().get(func)




def parse_apikey(account, force_api_key):
    """
    获取厂家api_key
    :param account:
    :param force_api_key:
    :return:
    """
    mb_ak = _account_cache.send_cmd(*get_mb_key(account))
    if mb_ak:
        #对于第三方帐号，必须都有key
        return mb_ak.split(':')[-1]
    return force_api_key or beiqi_keys.keys()[0]


def parse_sms_switch(api_key, sms_type):
    """
    短信开关
    例如青春之歌要求不发送sos短信
    :param api_key:
    :param sms_type:
    :return:
    """
    if not api_key or api_key in beiqi_keys:
        return True
    ob = oem_accounts.get(api_key)
    if ob is None:
        raise ValueError('parse_sms_switch: %s not exist' % api_key)

    switch = ob.get('sms_switch')
    if switch is None:
        return True
    return (switch >> sms_type) & 0b1


def handle_msg(p):
    """
    入口函数
    :param p:
    """
    # logger.debug('sms p: {0}, type(p)={1}'.format(p, type(p)))

    mobile = p.get('n')
    # tel or val
    params = p.get('p')
    account = p.get('a')
    # sms type
    typ = p.get('t')

    api_key = parse_apikey(account, p.get('k'))
    logger.debug('api_key=%r' % api_key)

    body = tr_txt(sms_template, typ, *params)

    logger.debug('sms_notify, mobile=%r, params=%r, account=%r, typ=%r, api_key=%r, body=%r' % (mobile, params, account, typ, api_key, body))

    sms_func(api_key)(mobile or account.split('@')[0], body)
