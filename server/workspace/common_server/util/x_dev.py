#coding:utf-8

import struct
from bit import encode_bits, decode_bits
from convert import bs2unichar, unichr2bs
from datetime import datetime


#python dict对象与设备可交换数据格式
#暂不支持list/tuple数据类型
#暂不支持浮点数key&value类型

TYPE_BIT_LEN = 0b1111
MAX_PAYLOAD_LEN = (0b111 << 8) | 0xff

DEV_TYPE = {
    'byte': 1,
    'short': 2,
    'int_3': 3,
    'int_4': 4,
    'long_5': 5,
    'long_6': 6,
    'long_7': 7,
    'long_8': 8,
    'ts': 9,
    'str': 10,
    'embed': 11,
}

    
def _long_type(l):
    if not isinstance(l, (int, long)):
        raise ValueError('x_dev l not int: {0}'.format(l))
    if l <= 0xff:
        return 1
    if l <= 0xffff:
        return 2
    if l <= 0xffffff:
        return 3
    if l <= 0xffffffff:
        return 4
    if l <= 0xffffffffff:
        return 5
    if l <= 0xffffffffffff:
        return 6
    if l <= 0xffffffffffffff:
        return 7
    return 8


#可交换的设备文件格式
def _encode_dev(s, is_key):
    if not isinstance(is_key, bool):
        raise ValueError('is_key not bool: {0}'.format(is_key))
    if is_key:
        s = str(s)

    if is_key:
        if not isinstance(s, basestring):
            raise ValueError('s not bs: {0}'.format(s))
        s = bs2unichar(s)
        len_ = len(s)
        #2**6
        if not len_ <= 64:
            raise ValueError('s too long: %s' % s)
        return '{0}{1}'.format(struct.pack('>B', len_), s)

    if s is None:
        s = ''
    if isinstance(s, basestring):
        s = bs2unichar(s)
        len_ = len(s)
        if not len_ <= MAX_PAYLOAD_LEN:
            raise ValueError('len_ too long: %d' % len_)
        return '{0}{1}'.format(struct.pack('>H', (0x8000 | (DEV_TYPE.get('str') << 11) | len_)), s)
    if isinstance(s, (int, long)):
        typ = _long_type(s)
        return '{0}{1}'.format(struct.pack('>H', (0x8000 | (typ << 11) | typ)), encode_bits(s, typ))
    if isinstance(s, dict):
        typ = DEV_TYPE.get('embed')
        _ = dumps(s)
        return '{0}{1}'.format(struct.pack('>H', (0x8000 | (typ << 11) | len(_))), _)

    raise ValueError('unsupported value type: {0}'.format(type(s)))


def dumps(d):
    """
    dict对象编码设备格式
    """
    if not isinstance(d, dict):
        raise ValueError('unsupported type: {0}'.format(type(d)))
    return ''.join(('{0}{1}'.format(_encode_dev(k, True), _encode_dev(v, False)) for k, v in d.iteritems()))
    

def _dev_decode(s, is_key):
    if not isinstance(is_key, bool):
        raise ValueError('is_key not bool: {0}'.format(is_key))
    if not (s and isinstance(s, str)):
        raise ValueError('s not str: {0}'.format(s))

    len_ = len(s)
    if is_key:
        if not len_ >= 2:
            raise ValueError('key %r too short' % s)

        head = decode_bits(s[0], 1)
        if not head <= 64:
            raise ValueError('key flag invalid')
        if len_ != head + 1:
            raise ValueError('invalid key: %r' % s)
        return unichr2bs(s[1:])

    if not len_ >= 3:
        raise ValueError('value %r too short' % s)
    head = decode_bits(s[:2], 2)
    if not 1 == head >> 15:
        raise ValueError('value flag invalid')

    typ = (head >> 11) & TYPE_BIT_LEN
    payload_len = head & MAX_PAYLOAD_LEN
    if len_ != payload_len + 2:
        raise ValueError('invalid value: %r' % s)

    if typ <= 8:
        return decode_bits(s[2:], typ)
    if 9 == typ:
        return datetime.fromtimestamp(decode_bits(s[2:], 4))
    if 10 == typ:
        #str
        return unichr2bs(s[2:])
    if 11 == typ:
        return loads(s[2:])
    raise ValueError('unsupported value type: {0}'.format(typ))


def loads(s):
    """
    解析编码字符串
    :param s:
    :return: :raise ValueError:
    """
    if not (s and isinstance(s, str)):
        raise ValueError('s not str: {0}'.format(s))

    d = {}
    while 1:
        if not s:
            break

        key_len = 1 + decode_bits(s[0], 1)
        key = _dev_decode(s[: key_len], True)

        value_len = decode_bits(s[key_len: key_len + 2], 2)
        value_len = (value_len & MAX_PAYLOAD_LEN) + 2
        value = s[key_len: key_len + value_len]
        value = _dev_decode(value, False)

        s = s[key_len + value_len:]
        d.update({key: value})
    return d
