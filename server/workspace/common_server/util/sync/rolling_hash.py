#coding:utf-8

#需pip install cython
import pyximport
pyximport.install()

from speed_sum import sumbytes
from hashlib import md5
import struct


#adler32取模值
MOD_ADLER = 65521


def rollhash_nomod(buf):
    """
    不取模，用于移动计算
    """
    assert buf and isinstance(buf, str)
    b = 0

    a = sumbytes(buf) + 1
    for i in xrange(len(buf)):
        b += sumbytes(buf[0: i+1]) + 1
    return b, a
    
    
def _rh2a(rht, to_hex=False):
    """
    转换tuple到ascii码
    :param rht: rolling hash tuple
    """
    assert rht and isinstance(rht, tuple) and 2 == len(rht)
    b, a = rht
    b %= MOD_ADLER
    a %= MOD_ADLER
    _ = (b << 16) | a
    if not to_hex:
        return _
    return '{0:08x}'.format(_)    


def rollhash_once(buf, to_hex=False):
    """
    计算rolling hash
    ref to http://en.wikipedia.org/wiki/Adler-32
    注意zlib.adler32算法没有+1
    """
    return _rh2a(rollhash_nomod(buf), to_hex)


def rollhash_x(prev_ht, rm_c, new_c, block_size, to_hex=False, tasc=True):
    """
    性能优化版
    :param prev_ht: previous hash tuple，没有对MOD_ADLER取模
    :param rm_c: 前一次计算的第一个字符
    :param new_c: 新计算的添加字符
    :param block_size: 块大小
    :param tasc: 计算为ascii值
    """
    assert prev_ht and isinstance(prev_ht, tuple) and 2 == len(prev_ht)
    assert isinstance(rm_c, str) and 1 == len(rm_c)
    assert isinstance(new_c, str) and 1 == len(new_c)

    b, a = prev_ht
    a += ord(new_c) - ord(rm_c)
    b = b - block_size * ord(rm_c) - 1 + a

    b %= MOD_ADLER
    a %= MOD_ADLER
    
    #优先级更高
    if not tasc:
        return b, a

    _ = (b << 16) | a
    if not to_hex:
        return _
    return '{0:08x}'.format(_)


def gen_hashtab(fs, block_size=128):
    """
    根据文件流生成hash表

    :param fs: 文件字符串
    :param block_size: 文件块大小，目前按照固定大小划分，以后可能动态生成
    """
    if not fs:
        return {
            'r': (),
            'md5': (),
            'bs': block_size,
            'bc': 0,
            'ls': 0,
        }

    assert isinstance(fs, str)

    def __():
        for b in xrange(0, len(fs), block_size):
            part = fs[b: b+block_size]
            yield rollhash_once(part, True), md5(part).hexdigest()

    roll_md5_list = tuple(__())

    divide = len(fs) / block_size
    mod = len(fs) % block_size

    return {
        'r': tuple((_[0] for _ in roll_md5_list)),
        'md5': tuple((_[1] for _ in roll_md5_list)),
        'bs': block_size,
        'bc': divide + (1 if mod else 0),
        'ls': mod or block_size,
    }


def build_asm(raw_fs, **hashtab):
    """
    创建重组文件

    :param raw_fs: 待同步的文件
    :param hashtab: hash表，必须包含相应键值
    """
    if not raw_fs:
        return ''

    assert isinstance(raw_fs, str)
    if 'r' not in hashtab or 'md5' not in hashtab:
        return ''

    #构建hash表,值与索引的映射
    rolling_map = dict(((_, idx) for idx, _ in enumerate(hashtab.get('r'))))
    md5_map = dict(((_, idx) for idx, _ in enumerate(hashtab.get('md5'))))

    def __():
        cursor = 0
        #收集不同的部分
        uneq = []
        #block size
        bs = hashtab.get('bs')
        hash_nomod = None
        while 1:
            if cursor >= len(raw_fs):
                if uneq:
                    yield 'd{0}{1}'.format(struct.pack('>H', len(uneq)), ''.join(uneq))
                break

            part = raw_fs[cursor: cursor + bs]
            #上一次已匹配到hash值
            if not uneq:
                rh = rollhash_once(part, True)
            else:
                #需要移动窗口时，先计算上一次tuple
                if hash_nomod is None:
                    hash_nomod = rollhash_nomod(part)
                else:
                    hash_nomod = rollhash_x(hash_nomod, uneq[-1], part[-1], bs, tasc=False)
                rh = _rh2a(hash_nomod, True)

            rh_index = rolling_map.get(rh)
            if rh_index is not None:
                md5_index = md5_map.get(md5(part).hexdigest())
                if md5_index is not None:
                    if uneq:
                        yield 'd{0}{1}'.format(struct.pack('>H', len(uneq)), ''.join(uneq))
                        uneq = []
                    cursor += bs
                    yield 'e{0}'.format(struct.pack('>I', md5_index))
                    hash_nomod = None
                else:
                    uneq.append(raw_fs[cursor])
                    cursor += 1
            else:
                uneq.append(raw_fs[cursor])
                cursor += 1

    return ''.join(__())


def asm_new(asm, old_fs, block_size=128):
    """
    根据重组文件，重新生成文件

    :param asm: 重组文件
    :param old_fs: 旧文件流
    :param block_size: 文件块大小
    """
    if not asm:
        return ''

    assert isinstance(asm, str)
    if old_fs:
        assert isinstance(old_fs, str)

    def __():
        prefix = 0
        while 1:
            if prefix >= len(asm):
                break

            c = asm[prefix]
            if 'd' == c:
                len_ = struct.unpack('>H', asm[prefix + 1: prefix + 3])[0]
                part = asm[prefix + 3: prefix + 3 + len_]
                if len_ != len(part):
                    raise ValueError('data part invalid')
                yield part
                prefix += 3 + len_
            elif 'e' == c:
                index = struct.unpack('>I', asm[prefix + 1: prefix + 1 + 4])[0]
                part = old_fs[block_size * index: block_size * (index + 1)]
                if not part:
                    raise ValueError('exist part invalid')
                yield part
                prefix += 1 + 4
            else:
                raise ValueError('unknown prefix: %r' % prefix)

    return ''.join(__())
