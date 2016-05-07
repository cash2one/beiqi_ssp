#coding:utf-8
from utils import logger
from datetime import datetime
from langs import date_langs, _mcc_map, time_langs, DEFAULT_LANG
from util.oem_account_key import beiqi_keys, oem_accounts
from util.redis.redis_client import Redis
from util.stream_config_client import load as conf_load
from util.sso.dev_active import get_dev_imeiimsi_etc
from util.convert import is_num, pretty_unit


dev_filter = Redis(dict(conf_load('redis.ini')).get('redis.ini').get('dev_filter', 'url'))
CHINA_AREA = {'chs', 'cht'}


def resolve_lang(mcc=None, api_key=None, pid=None):
    """
    多语言翻译策略:
    1. 设备mcc
    2. 无mcc的设备，以帐号api_key优先
    :param mcc:
    :param api_key:
    :param pid:
    """
    if mcc is not None:
        return _mcc_map.get(mcc, DEFAULT_LANG)
    if api_key is not None:
        if api_key in beiqi_keys:
            return DEFAULT_LANG
        d = oem_accounts.get(api_key)
        if d is not None:
            return d.get('tr') or DEFAULT_LANG
        logger.warn('tr key {0} not found'.format(api_key))
        return DEFAULT_LANG
    if pid is not None:
        etc = dev_filter.send_cmd(*get_dev_imeiimsi_etc(pid))
        if not etc:
            return DEFAULT_LANG
        query_mcc = etc.split(':')[0]
        return resolve_lang(mcc=int(query_mcc)) if is_num(query_mcc) else DEFAULT_LANG

    raise ValueError('at least one arg required')


def is_not_china(lang):
    """
    不是天朝
    :param lang:
    :return:
    """
    return lang not in CHINA_AREA


def tr_timespan(lang, seconds):
    """
    翻译时间间隔
    """
    units = time_langs.get(lang) or time_langs.get(DEFAULT_LANG)
    #类似越南语每个字符必须有空格，strip处理掉头尾的空格
    return ''.join(pretty_unit(units, seconds)).strip()


def tr_date(lang, d):
    """
    翻译日期
    :param lang: 语言类型
    :param d: 日期对象
    """
    #datetime类型无法用msgpack序列化，int用于兼容
    if isinstance(d, int):
        d = datetime.fromtimestamp(d)
    if isinstance(d, datetime):
        fmt = date_langs.get(lang)
        if fmt is None:
            fmt = date_langs.get(DEFAULT_LANG)
        return d.strftime(fmt)
    raise ValueError('unknown date: {0}'.format(d))


def tr_txt(template, cat, *params):
    """
    翻译文本
    各参数含义见sms_template注释
    :param template: 语言模板
    :param cat: 类别
    :param params: 调用参数
    """
    if not isinstance(template, dict):
        raise ValueError('template invalid: {0}'.format(template))
    d = template.get(cat)
    if d is None:
        raise ValueError('lang cat not found: {0}'.format(cat))

    return (d.format(*params))
