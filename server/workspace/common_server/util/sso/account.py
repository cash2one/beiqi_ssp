#coding:utf-8


from base64 import standard_b64encode
import hashlib
from util.oem_conv import get_mb_key, parse_oem_options, OEM_KEY_PATTERN
from util.convert import combine_redis_cmds, is_mobile
from util.oem_account_key import beiqi_keys
from itertools import izip


ACCOUNT_PREFIX = 'sso_account'
LINKTOP_PREFIX_4 = set((k[:4] for k in beiqi_keys.iterkeys()))
LINKTOP_ALL = set(beiqi_keys.iterkeys())
LOSTPWD_ACCOUNT_VAL = 'gen:account:lostpwd:val'
NEW_ACC_REG_VAL = 'gen:new_acc:reg:val'
SMS_SPEED_CONTROL = 'sms_speed_control'
USER_VERI_SMS_TIME = 'user_veri_sms_time'
EXPECTED_EXPIRE_TIME = 'expected_expire_time'


SMS_SPEED_INTERVAL = 1


def set_user_veri_sms_time(mobile, ts):
    key = ':'.join((USER_VERI_SMS_TIME, mobile))
    return ('set', key, ts), ('expire', key, 60)


def get_user_veri_sms_time(mobile):
    return 'get', ':'.join((USER_VERI_SMS_TIME, mobile))


def init_sms_speed():
    return ('set', SMS_SPEED_CONTROL, 1), ('expire', SMS_SPEED_CONTROL, 1)

def get_sms_speed():
    return 'get', SMS_SPEED_CONTROL


def incr_sms_speed():
    return 'incr', SMS_SPEED_CONTROL


def gen_newacc_reg_val(mobile, code, api_key):
    assert mobile and isinstance(mobile, str)
    assert code and isinstance(code, str)

    key = ':'.join((NEW_ACC_REG_VAL, mobile))
    value = ':'.join((code, api_key))
    return ('set', key, value), ('expire', key, 900)


def get_newacc_reg_val(mobile):
    assert mobile and isinstance(mobile, str)
    key = ':'.join((NEW_ACC_REG_VAL, mobile))
    return 'get', key


def pass_lostpwd_val(cur_account):
    assert cur_account and isinstance(cur_account, str)
    return 'delete', ':'.join((LOSTPWD_ACCOUNT_VAL, cur_account))


def review_lostpwd_val(cur_account):
    assert cur_account and isinstance(cur_account, str)
    return 'get', ':'.join((LOSTPWD_ACCOUNT_VAL, cur_account))


def gen_lostpwd_val(cur_account, val):
    assert cur_account and isinstance(cur_account, str)
    assert val and isinstance(val, str)

    key = ':'.join((LOSTPWD_ACCOUNT_VAL, cur_account))
    return ('set', key, val), ('expire', key, 900)


def get_pwd(account):
    """
    获取密码
    :param account:
    :return:
    """
    assert account and isinstance(account, str)
    return 'get', ':'.join((ACCOUNT_PREFIX, account))


def exist_account(account):
    """
    帐号已存在
    :param account:
    :return:
    """
    assert account and isinstance(account, str)
    return 'exists', ':'.join((ACCOUNT_PREFIX, account))


def cipher_pwd(pwd):
    """
    密码加密
    :param pwd:
    :return:
    """
    return standard_b64encode(hashlib.sha1(pwd).digest())


def set_account_pwd(account, pwd, setnx=True):
    """
    创建帐号，密码
    :param account:
    :param pwd:
    :param setnx:
    :return:
    """
    assert account and isinstance(account, str)
    assert pwd and isinstance(pwd, str)
    if setnx:
        return 'setnx', ':'.join((ACCOUNT_PREFIX, account)), pwd
    return 'set', ':'.join((ACCOUNT_PREFIX, account)), pwd


def _extract_mobiles(accounts):
    if not accounts:
        return None
    if isinstance(accounts, str):
        mobile = accounts.partition('@')[0]
        return mobile if is_mobile(mobile) else None
    if not isinstance(accounts, (list, tuple)):
        raise ValueError('unsupported type: %s' % type(accounts))
    if 1 == len(accounts):
        return _extract_mobiles(accounts[0])
    return [_extract_mobiles(x) for x in accounts]


def _build_redis_cmd(accounts):
    if isinstance(accounts, str):
        return get_mb_key(accounts)
    return [get_mb_key(x) for x in accounts]


def _yield_multi(redis_result, accounts):
    if not isinstance(redis_result, (list, tuple)):
        raise ValueError('redis_result invalid: {0}'.format(redis_result))
    if not isinstance(accounts, (list, tuple)):
        raise ValueError('accounts invalid: {0}'.format(accounts))

    for rr, single_acc in izip(redis_result, accounts):
        if not rr:
            yield _extract_mobiles(single_acc)
            continue
        mobile, _ = rr.split(':')
        yield mobile if is_mobile(mobile) else None


def get_mobile(sync_account_redis, api_key, accounts):
    """
    根据帐号获取手机号
    多个accounts,返回多个

    :param accounts: 同时支持单个str和list参数
    :param api_key:
    :param sync_account_redis: 同步redis对象
    :return:
    """
    if api_key and ':' in api_key:
        raise ValueError('wrong arg: %s' % api_key)
    if not isinstance(accounts, (str, list, tuple)):
        raise ValueError('unsupported type: {0}'.format(accounts))

    if not api_key:
        return _extract_mobiles(accounts)
    if api_key in LINKTOP_PREFIX_4 or api_key in LINKTOP_ALL:
        #能命中凌拓key
        return _extract_mobiles(accounts)

    parse_result = parse_oem_options(api_key)
    if not parse_result:
        #非oem帐号
        return _extract_mobiles(accounts)

    _, _, lt_acc, sms, has_mobile, _ = parse_result
    if lt_acc:
        #是凌拓帐号
        return _extract_mobiles(accounts)

    if not has_mobile:
        if isinstance(accounts, str):
            return None
        return (None, ) * len(accounts)

    redis_result = sync_account_redis.send_multi_cmd(*combine_redis_cmds(_build_redis_cmd(accounts)))
    ll = tuple(
        _yield_multi(
            (redis_result,) if (isinstance(redis_result, str) or not redis_result) else redis_result,
            (accounts,) if isinstance(accounts, str) else accounts
        )
    )
    if isinstance(accounts, (list, tuple)):
        return ll
    _ = ll[0]
    del ll
    return _


def set_login_expire(username, expire):
    return 'hset', EXPECTED_EXPIRE_TIME, username, expire
