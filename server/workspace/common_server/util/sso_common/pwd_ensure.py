#coding:utf-8


from util.oem_account_key import oem_accounts, beiqi_keys
from util.oem_conv import parse_oem_options
from util.log_util import gen_log
from common.decode_3rd import check_cipher


def _select_lt_oem(api_key):
    _0 = beiqi_keys.get(api_key)
    _1 = oem_accounts.get(api_key)

    if not _0 and not _1:
        gen_log.warn('{0} not found'.format(api_key))
        return None

    if _0:
        return 1, _0, False
    return parse_oem_options(_1.get('opt_mask') or api_key)[0], _1, True


def lost_parse(api_key, auth_cipher, sign, ver=1):
    need_sms_code = _select_lt_oem(api_key)
    if need_sms_code is None:
        return 3

    need_sms_code, api_ob, is_oem = need_sms_code
    plain = check_cipher(auth_cipher, api_ob.get('s'), sign)
    if not plain:
        return 1

    account = plain.get('acc')
    old_pwd = plain.get('old_pwd')
    new_pwd = plain.get('new_pwd')

    if not need_sms_code:
        if not (old_pwd and new_pwd and old_pwd != new_pwd):
            gen_log.warn('old/new pwd missing, or eq: {0}, {1}'.format(old_pwd, new_pwd))
            return 3
        return 0, account, old_pwd, new_pwd, is_oem
    return 2, account, None, None, is_oem


def new_parse(api_key, auth_cipher, sign, ver=1):
    need_sms_code = _select_lt_oem(api_key)
    if need_sms_code is None:
        #参数错误
        return 3

    need_sms_code, api_ob, is_oem = need_sms_code
    if not need_sms_code:
        #不需要验证码
        gen_log.warn('{0} not need sms_pwd_new'.format(api_key))
        return 1

    plain = check_cipher(auth_cipher, api_ob.get('s'), sign)
    if not plain:
        return 3

    return [plain.get(k) for k in ('acc', 'val', 'new_pwd')]
