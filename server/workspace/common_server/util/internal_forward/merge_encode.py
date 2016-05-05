#coding:utf-8


from util.convert import redis_encode_batch
from . import prepend_head


@prepend_head
def encode(lang, mobile, ts, account, typ, delay=600):
    """
    合并短信编码
    :param lang: 翻译语言
    :param mobile:
    :param ts:
    :param account: 通过帐号判定使用谁家的短信通道
    :param typ:
    :param delay:
    :return:
    """
    if not (ts and isinstance(ts, int)):
        raise ValueError('ts not time')
    if not (delay and isinstance(delay, int)):
        raise ValueError('delay not int')
    #帐号默认为空，新增参数，兼容之前无帐号调用
    return redis_encode_batch(lang, mobile, ts, account, typ, delay)