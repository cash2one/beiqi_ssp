# coding:utf-8


import random
import re

from bit import span_bits
from convert import take_offset_chars
from crypto_rc4 import encrypt, decrypt


dev_id_mask_pool = 'ca81250b5b53477a8759ac889865a3e74446a367fd4146f6b917686cad24ce' \
                   '43b6ac163e9b654292b7fcda1968ebe48252dce2704fc04f9183aa31871e339a8e'
#会话密钥
dev_id_session_pool = 'b13c1b38f4de4986be572c5bd1078497aa138725b8ed4b24b3edae9b1e5' \
                      '3f4555a0f2de8564648a783c9ae41654754ba63eb6de5f799472b91027a44c0113690'

# 外部模块，例如pt30算法
ext_id_mask_pool = '7191a404c1654e15a2a7a17928ebfa87d90d47d4a31b437c9d4d5c17b023e03' \
                   '35a96a1480bef48c6ad8af96cd228ae8ec4c78caaba904170973f1ee26fd5a29c'

_qp = re.compile(r'^[a-f\d]{1,8}$', re.I)
# 后5比特表示设备类型
DEV_TYPE_BITS = 0x1f


def rand_mask_offset():
    """
    激活设备时使用
    """
    return random.randint(0, len(dev_id_mask_pool) - 1)


def mask(pid, id_pool, id_offset=-1, s_offset=-1):
    """
    对id做加密处理，例如pt30设备端会话id，以及pt30算法模块

    :param pid: 设备id
    """
    assert pid and isinstance(pid, str) and 8 == len(pid)
    assert id_pool and isinstance(id_pool, str)

    if -1 == id_offset:
        id_offset = random.randint(0, len(id_pool) - 1)
    assert isinstance(id_offset, int) and 0 <= id_offset <= len(id_pool) - 1

    r = encrypt(pid, take_offset_chars(id_pool, id_offset, 16))
    r = '{0}{1:02x}'.format(r, id_offset)

    if -1 == s_offset:
        s_offset = random.randint(0, 127)
    assert isinstance(s_offset, int) and 0 <= s_offset <= 127

    return '{0}{1:02x}'.format(r, s_offset)


def unmask(cipher, id_pool):
    """
    设备id解密
    """
    assert cipher and isinstance(cipher, str)

    cl = len(cipher)
    assert 18 <= cl <= 20

    id_offset = int(cipher[16: 18], 16)
    session_offset = cipher[18: 20]
    session_offset = -1 if not session_offset else int(session_offset, 16)

    assert 0 <= id_offset <= len(id_pool) - 1
    return decrypt(cipher[:16], take_offset_chars(id_pool, id_offset, 16)), id_offset, session_offset


def parse_io_options(bits, split=True):
    """
    io选项在绑定设备和用户关系时需要提取，其他时候用不到
    id格式的转换需要把io选项排除在外

    :param split: io选项拆分
    """
    assert isinstance(bits, int) and bits <= 0b111
    if not split:
        return bits
    # 数据，短信，蓝牙
    return span_bits(bits, 2, 0, 0)


def rawid_tuple(pid, with_io=False):
    """
    查询参数转换为type和10进制id
    
    :param pid: str, 010000ff -> 1, 0xff
    :param with_io: 是否包含io选项
    :return pid, typ, sn, io
    """
    if not pid or not isinstance(pid, str) or not _qp.search(pid):
        return None

    first = int(pid[:-6] or '0', 16)
    _2nd = int(pid[-6:], 16)
    pid = '{0:02x}{1:06x}'.format(first, _2nd)
    if not with_io:
        return pid, first & DEV_TYPE_BITS, _2nd
    return pid, first & DEV_TYPE_BITS, _2nd, parse_io_options(first >> 5, False)


def tuple_rawid(io, typ, sn):
    """
    :param io: io选项
    :param typ: 类型
    :param sn: 序号
    """
    if isinstance(io, int):
        assert 0 <= io <= 0b111
    else:
        assert isinstance(io, tuple) and 3 == len(io)
        io = (io[0] << 2) | (io[1] << 1) | io[2]
    assert isinstance(typ, int) and 0 <= typ <= 0b11111
    assert isinstance(sn, int) and 0 <= sn <= 0xffffff

    return (io << 29) | (typ << 24) | sn