#coding:utf-8

import struct

FMT = {
    1: 'B',
    2: 'H',
    4: 'I',
}


def span_bits(i, b, e, cal=1):
    """提取二进制比特位
    末尾为0
    
    :param i: 整数
    :param b：开始比特位
    :param e：最后比特位
    :param cal: 1为计算值，0为提取单个比特位
    """
    if not isinstance(i, (int, long)):
        raise ValueError('i should be int, actual is {0}'.format(i))
    if not isinstance(b, int) or not isinstance(e, int) or b < e:
        raise ValueError('b/e invalid: {0}, {1}'.format(b, e))

    offset = b - e + 1

    v = i >> e
    v &= 2 ** offset - 1

    if cal:
        return v

    r = [int(x) for x in bin(v)[2:]]
    return tuple([0, ] * (offset - len(r)) + r)


def encode_bits(num, count):
    """按大端对整数编码
    :param num: int
    :param count: 编码字节数
    """
    if count in FMT:
        return struct.pack('>{0}'.format(FMT.get(count)), num)

    l = []
    for i in xrange(count, 0, -1):
        l.append(struct.pack('>B', (num >> (8 * (i - 1))) & 0xff))

    return ''.join(l)


def decode_bits(enc, count):
    """按大端对字符串解码
    :param enc: 已编码字符串
    :param count: 解码字节数
    """
    if not count or not isinstance(count, int):
        raise ValueError('count should be int: %r' % count)

    if not enc or not isinstance(enc, str) or len(enc) != count:
        raise ValueError('invalid encoded bits: %r' % enc)

    r = (struct.unpack('>B', x)[0] for x in enc)
    r = ((v << (8 * (count - i - 1))) for i, v in enumerate(r))

    return sum(r)
