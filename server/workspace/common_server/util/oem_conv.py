#coding:utf-8


import re
from uuid import uuid4
from bit import span_bits
from oem_account_key import oem_accounts
from convert import is_email


OEM_KEY_PATTERN = re.compile(r'^[a-f\d]{4,32}$')
OEM_ACC_MAP = 'oem:acc2mb:acc2key'


def fix_account_postfix(account):
    if is_email(account):
        return account
    return ''.join((account, '@beiqi.com.cn'))


def create_oem_account(pwd_new_code, push_or_not, lt_acc, sms, has_mobile, has_pwd):
    """
    创建oem帐号，key前2字节表示
    凌拓帐号注册需通过手机号验证激活
    虚拟帐号可直接激活，但如果需要代发短信（山西移动）

    :param pwd_new_code: 密码通过验证码找回
    :param push_or_not: 是否有批量推送
    :param lt_acc: 是否使用凌拓帐号，需要短信验证，即使是oem帐号
    :param sms: 后续是否短信，例如关注，sos录音等
    :param has_mobile: 虚拟帐号是否已绑定手机号
    :param has_pwd: 有密码
    """
    if not sms:
        pwd_new_code = 0
    if lt_acc:
        pwd_new_code = 1
    if not has_pwd:
        pwd_new_code = 0

    head = int(pwd_new_code) << 5 \
        | int(push_or_not) << 4 \
        | int(lt_acc) << 3 \
        | int(sms) << 2 \
        | int(has_mobile) << 1 \
        | has_pwd
    #oem帐号
    head |= 1 << 15
    #版本：1
    head |= 1 << 12
    return ''.join(('%02x' % head, uuid4().get_hex()[4:])), uuid4().get_hex()


def parse_oem_options(api_key):
    """
    解析oem帐号选项
    :param api_key:
    """
    if not isinstance(api_key, str):
        return None
    if not OEM_KEY_PATTERN.search(api_key):
        #正则已修改
        return None

    if api_key.startswith('a685'):
        #兼容山西旧key
        api_key = '9006'

    head = int(api_key[:4], 16)
    #版本
    ver = span_bits(head, 15, 12)
    if not (ver >> 3):
        return None

    ver &= 0b111
    #todo: 检查版本号
    #短信相关选项。批量推送，凌拓帐号，短信，手机号码，密码
    return span_bits(head, 5, 0, 0)


def is_oem_account(api_key):
    """
    是否oem帐号
    :param api_key:
    """
    return api_key in oem_accounts


def get_mb_key(account):
    """
    根据帐号手机号
    :param account:
    :return: :raise ValueError:
    """
    if not is_email(account):
        raise ValueError('account invalid: {0}'.format(account))
    return 'get', ':'.join((OEM_ACC_MAP, account))


def get_mobile_key_list(multi_accounts):
    """
    获取多个手机号
    :param multi_accounts:
    :raise ValueError:
    """
    if not isinstance(multi_accounts, (list, tuple)):
        raise ValueError('multi accounts invalid: {0}'.format(multi_accounts))
    return (('get', ':'.join((OEM_ACC_MAP, x))) for x in multi_accounts)


def map_account_mobile_oem_key(api_key, account, mobile):
    """
    创建帐号、手机号与api_key的映射关系
    :param api_key:
    :param account:
    :param mobile:
    """
    if not (isinstance(api_key, str) and OEM_KEY_PATTERN.search(api_key)):
        raise ValueError('api_key invalid: {0}'.format(api_key))
    if not isinstance(account, str):
        raise ValueError('account invalid: {0}'.format(account))

    mobile = mobile or ''
    return 'set', ':'.join((OEM_ACC_MAP, account)), ':'.join((mobile, api_key))