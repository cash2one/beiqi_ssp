#coding:utf-8


from util.convert import redis_encode_batch
from . import prepend_head


@prepend_head
def encode(*files):
    """
    支持多个文件名
    带有文件后缀
    :param files: 带后缀的文件名
    """
    return redis_encode_batch(*files)