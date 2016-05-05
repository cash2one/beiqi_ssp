#coding:utf-8


import struct
from util.bit import encode_bits


def _single_block(fn, body):
    """
    单个文件块
    :param fn: 文件名
    :param body: 文件体
    :return:
    """
    if not isinstance(fn, str) and len(fn) <= 0xff:
        raise ValueError('fn invalid: {0}'.format(fn))
    return ''.join((
        struct.pack('>B', len(fn)),
        fn,
        body
    ))


def cat_files(file_blocks):
    """
    :param file_blocks: 多文件块，键为文件名
    """
    if not (isinstance(file_blocks, dict) and len(file_blocks) <= 0xff):
        raise ValueError('file_blocks invalid: {0}'.format(file_blocks))

    tot_blocks = [_single_block(k, v) for k, v in file_blocks.iteritems()]
    if not tot_blocks:
        return ''
    return ''.join((
        'MF',
        struct.pack('>B', len(file_blocks)),
        ''.join((encode_bits(len(x), 3) for x in tot_blocks)),
        ''.join(tot_blocks),
    ))