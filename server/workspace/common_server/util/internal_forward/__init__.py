#coding:utf-8


import struct


def prepend_head(func):
    """
    系统内部协议转发，统一使用redis编码协议
    """
    def __(*args):
        s = func(*args)
        return ''.join(('*1{0}'.format(struct.pack('>I', len(s))), s))

    return __