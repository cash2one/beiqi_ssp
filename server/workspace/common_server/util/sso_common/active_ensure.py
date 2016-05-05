#coding:utf-8


from util.oem_account_key import oem_accounts, beiqi_keys
from utils import logger
from util.oem_conv import parse_oem_options, fix_account_postfix
from util.convert import is_mobile
from decode_3rd import check_cipher


def validate(api_key, auth_cipher, sign, ver=1):
    """
    :param api_key: 开发者key
    :param auth_cipher:
    """
    api_ob = tuple((x for x in (oem_accounts.get(api_key), beiqi_keys.get(api_key)) if x))
    if not api_ob:
        #api_key未找到
        logger.warn('no api_key {0}'.format(api_key))
        return 4

    api_ob = api_ob[0]
    plain = check_cipher(auth_cipher, api_ob.get('s'), sign)
    if not plain:
        return 4

    acc = plain.get('acc')
    code = plain.get('code')
    pwd = plain.get('pwd')

    if not (acc and code and pwd):
        logger.warn('params lost in {0}'.format(plain))
        return 5

    acc = acc.split('@')[0]
    if not is_mobile(acc):
        logger.warn('acc not mobile: {0}'.format(acc))
        return 3

    acc = fix_account_postfix(acc)
    if api_key in beiqi_keys:
        return False, api_key, acc, code, pwd

    parse_result = parse_oem_options(api_ob.get('opt_mask') or api_key)
    if not parse_result:
        return 1

    _, _, lt_acc, _, _, has_pwd = parse_result
    if not (lt_acc and has_pwd):
        logger.warn('not lt_acc, active refuse: {0}'.format(api_key))
        return 1

    return True, api_key, acc, code, pwd
