#coding:utf-8

from util.convert import redis_encode_batch
from . import prepend_head


#例如用户profile
APP_APP = 0b0
#例如英语学习
SERVER_APP_DEV = 0b10 | 0b1000
#例如双向语音
APP_DEV = 0b100
#例如录音上传
DEV_APP = 0b10000
#需要过期的类型
NEED_EXPIRE = (2, 4)


def resolve_expire(file_src):
    """
    是否过期解析
    """
    if not isinstance(file_src, int):
        raise ValueError('file_src not int, but %s' % type(file_src))
    if file_src > DEV_APP:
        raise ValueError('unsupported source: %x' % file_src)
    for x in NEED_EXPIRE:
        if (file_src >> x) & 0b1:
            return 86400
    return 0


@prepend_head
def encode(cmd, expire, lvl_fn, lvl_body=None):
    """
    leveldb请求编码
    :param cmd: 执行动作，get/put/snapshot
    :param expire: 文件有效期，0表示长期有效，单位秒
    :param lvl_fn: 文件名
    :param lvl_body: 文件体
    """
    if cmd not in ('get', 'put', 'snapshot', 'delete'):
        raise ValueError('cmd invalid: {0}'.format(cmd))
    if not isinstance(expire, int):
        raise ValueError('expire not int, but %s' % type(expire))
    if not isinstance(lvl_fn, str):
        raise ValueError('lvl_fn invalid: {0}'.format(lvl_fn))
    if not (lvl_body is None or isinstance(lvl_body, str)):
        raise ValueError('lvl_body invalid: {0}'.format(lvl_body))

    return redis_encode_batch(cmd, expire, lvl_fn, lvl_body or '')
