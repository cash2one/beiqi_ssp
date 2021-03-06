# coding:utf-8

from datetime import datetime
import re
import time
import struct
from urlparse import urlparse
from types import GeneratorType, NoneType


TS_UNITS = ('year', 'month', 'day', 'hour', 'minute', 'sec')
_reg_val_code_pat = re.compile(r'^[\d]{6}$')
_follow_val_code_pat = re.compile(r'^[\d]{4}$')
_num_pat = re.compile(r'^-?[a-f\d]+?$', re.I)
_email_pat = re.compile(r'^(?P<name>[a-zA-Z\d][_\.a-zA-Z\d]*)@(?P<domain>[a-zA-Z\d.]+\.[a-z]{2,4})$')
_uuid_pat = re.compile(r'^[a-f\d]{32}$')
_sha1_pat = re.compile(r'^[a-f\d]{40}$')
# 能用到202x年已经太牛叉了
_date_pat = re.compile(
    r'^(?P<year>20[12]\d)-(?P<month>0[1-9]|1[012])-(?P<day>\d{1,2})(?:T(?P<hour>[01][0-9]|2[0-3]):(?P<minute>[0-5][0-9]):(?P<sec>[0-5][0-9]))?$')
_time_pat = re.compile(r'^(?P<hour>[01][0-9]|2[0-3]):(?P<minute>[0-5][0-9]):(?P<sec>[0-5][0-9])$')
_float_pat = re.compile(r'^-?\d+(\.\d+)?$')
_mac_pat = re.compile(r'^[a-f\d]{2}(?::[a-f\d]{2}){5}$', re.I)
_gsm_tid_pattern = re.compile(r'^[\d]{13}$', re.I)
_cdma_tid_pattern = re.compile(r'^[\da-f]{20}$', re.I)
_imei_pat = re.compile(r'^\d{15}$')
_imsi_pat = re.compile(r'^\d{15}$')
_ip_pat = re.compile(r'^(?:(?:\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.){3}(?:\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])$')
_port_pat = re.compile(r'^\d{4,5}$')
_ip_port_pat = re.compile(
    ''.join(('^', '(?P<ip>', _ip_pat.pattern[1:-1], '|[-_a-z.]+):(?P<port>', _port_pat.pattern[1:-1], ')$')))
_cn_mobile_pat = re.compile(r'^\d{9,12}$')
_cn_mobile_cdma = re.compile(r'^(?:(?:(?:133|153|177|18[019])\d{1})|1700)\d{7}$') #电信

def parse_ip_port(s):
    if not s or not isinstance(s, str):
        return None
    m = _ip_port_pat.search(s)
    if not m:
        return None
    port = int(m.groupdict().get('port'))
    if port > 0xffff:
        return None
    ip = m.groupdict().get('ip')
    return ip, port


def redis_encode_str(buf):
    if not isinstance(buf, (str, NoneType)):
        raise ValueError('buf not str or None: %s' % type(buf))
    if buf is None:
        return '$-1\r\n'
    return ''.join(('$', str(len(buf)), '\r\n', buf, '\r\n'))


def redis_encode_int(i):
    if not isinstance(i, (int, long)):
        raise ValueError('redis_encode_int not int: %s' % type(i))
    return ''.join((':', str(i), '\r\n'))


def redis_err(s):
    if not (s and isinstance(s, str)):
        raise ValueError('redis_err not str: %s' % type(s))
    return ''.join(('-', s, '\r\n'))


def __iter_redis_field(*fields):
    for f in fields:
        if f is None:
            yield redis_encode_str(None)
        if isinstance(f, (int, long)):
            yield redis_encode_int(f)
        elif isinstance(f, float):
            yield redis_encode_str(str(f))
        elif isinstance(f, str):
            yield redis_encode_str(f)
        elif isinstance(f, (tuple, list)) and 2 == len(f) and 'err' == f[0]:
            yield redis_err(f[1])


def redis_encode_batch(*fields):
    """
    错误格式：('err', 'str')
    """
    count = len(fields)
    if not count:
        return '*-1\r\n'
    return ''.join(('*{0}\r\n'.format(count), ''.join(__iter_redis_field(*fields))))


def is_reg_val_code(s):
    """
    帐号注册验证码
    """
    if not s or not isinstance(s, str):
        return False
    return _reg_val_code_pat.search(s)


def is_follow_val_code(s):
    """
    帐号关注验证码
    """
    if not s or not isinstance(s, str):
        return False
    return _follow_val_code_pat.search(s)


def is_mobile(s):
    if not s or not isinstance(s, str):
        return False
    return _cn_mobile_pat.search(s)


def is_mobile_cdma(s):
    """
    电信手机号码
    :param s:
    :return:
    ^133\d{8}$
    ^153\d{8}$
    ^177\d{8}$
    ^18[0|1|9]\d{8}$
    ^1700\d{7}$
    """
    if not s or not isinstance(s,str):
        return False
    return _cn_mobile_cdma.search(s)


def is_imsi(s):
    if not s or not isinstance(s, str):
        return False
    return _imsi_pat.search(s)


def is_imei(s):
    if not s or not isinstance(s, str):
        return False
    return _imei_pat.search(s)


def is_gsm_tid(tid):
    """移动终端号码"""
    if not tid or not isinstance(tid, str):
        return False
    return _gsm_tid_pattern.search(tid)


def is_cdma_tid(tid):
    """电信终端号码"""
    if not tid or not isinstance(tid, str):
        return False
    return _cdma_tid_pattern.search(tid)


def is_mac(s):
    """
    mac地址
    """
    if not s or not isinstance(s, str):
        return False
    return _mac_pat.search(s)


def is_time(v):
    if not v or not isinstance(v, str):
        return False
    return _time_pat.search(v)


def is_date(v):
    """
    20140424(T12:34:56)
    year, month, day, hour, minute, sec
    """
    if not v or not isinstance(v, str):
        return False
    m = _date_pat.search(v)
    if not m:
        return False

    month = int(m.groupdict().get('month'))
    day = int(m.groupdict().get('day'))
    if 2 == month and day > 29:
        return False
    return m


def first_default(func, seq):
    """
    惰性展开
    """
    if not callable(func):
        raise ValueError('func not func: %s' % type(func))
    for _ in seq:
        if func(_):
            return _
    return None


def gen_ts(v):
    """
    生成时间
    """
    m = is_date(v)
    if not m:
        return False
    return datetime(*(int(m.groupdict().get(u) or '0') for u in TS_UNITS))


def is_float(v):
    if not v or not isinstance(v, str):
        return False
    return _float_pat.search(v)


def is_num(v):
    if isinstance(v,int):
        return True
    if not v or not isinstance(v, str):
        return False
    return _num_pat.search(v)


def is_email(v):
    if not v or not isinstance(v, str):
        return False
    return _email_pat.search(v)


def is_uuidhex(v):
    if not v or not isinstance(v, str):
        return False
    return _uuid_pat.search(v)


def bs2unichar(bs):
    """
    basestring转换unicode16进制格式
    """
    if not isinstance(bs, basestring):
        raise ValueError('bs not basestring: {0}'.format(bs))
    if isinstance(bs, unicode):
        return ''.join((struct.pack('>H', ord(x)) for x in bs))
    return ''.join((struct.pack('>H', ord(x)) for x in bs.decode('utf-8')))


def is_even(n):
    """
    偶数判定
    """
    return 0 == n % 2


def unichr2bs(u):
    """
    unicode 16机制格式转化为basestring
    """
    if not (u and isinstance(u, str)):
        raise ValueError('unichr2bs not str: %s' % type(u))
    len_ = len(u)
    if not is_even(len_):
        raise ValueError('invalid unicode encoding: %r' % u)
    return u''.join((unichr(x) for x in struct.unpack('>{0}'.format('H' * (len_ / 2)), u)))


def bs2unicode(bs):
    """
    basestring转换为python unicode类型
    """
    if not isinstance(bs, basestring):
        return bs
    if isinstance(bs, unicode):
        return bs
    return bs.decode('utf-8')


def bs2utf8(bs):
    if isinstance(bs, basestring):
        return bs.encode('utf-8') if isinstance(bs, unicode) else bs
    return bs


def mac2long(mac):
    """
    mac地址转化为6字节long
    """
    if not is_mac(mac):
        raise ValueError('invalid mac: %s' % mac)

    parts = mac.split(':')
    r = 0
    for i, p in enumerate((int(p, 16) for p in parts)):
        r |= p << ((5 - i) * 8)
    return r


def take_offset_chars(s, offset, len_=16):
    """
    通过偏移量截取部分字符串

    :param s: 输入字符串
    :param offset: 偏移量
    :param len_: 生成密钥的长度
    """
    p = s[offset: len_ + offset]
    return '{0}{1}'.format(p, s[: len_ - len(p)])


def sms_pad(s):
    """
    把短信内容不足70个字符的后面补空格
    """
    if not (s and isinstance(s, str)):
        raise ValueError('sms_pad not str: %s' % type(s))
    l = 70 - len(s.decode('utf-8'))
    s += ' ' * l
    return s


def pad(s, ratio, postfix='\x00'):
    """
    按照比例补齐长度
    
    :param ratio: 按此整数倍补齐
    :param postfix: 补齐后缀
    """
    if not (s and isinstance(s, str)):
        raise ValueError('pad not str: %s' % type(s))
    mod = (len(s) % ratio) or ratio

    return '{0}{1}'.format(s, postfix * (ratio - mod))


postfix_pattern = re.compile(r'\x00*$')


def unpad(s):
    if not (s and isinstance(s, str)):
        raise ValueError('unpad not str: %s' % type(s))
    return postfix_pattern.sub('', s)


def combine_redis_cmds(*args):
    # 至少要求有一个
    if not args:
        raise ValueError('args at least 1')
    if not isinstance(args[0], (str, tuple, list, GeneratorType)):
        raise ValueError('actual is {0}'.format(type(args[0])))

    default = ()
    for x in args:
        if isinstance(x, GeneratorType):
            x = tuple(x)
        if isinstance(x[0], str):
            x = (x, )
        if not isinstance(x, tuple):
            x = tuple(x)
        default += x
    return default


def resolve_redis_url(url, with_channel=False):
    """解析redis字符串
    :param url: redis://<ip>:<port>/db,db,db?pwd=xxx#channel
    """
    url = urlparse(url)
    ip, port = url.netloc.split(':')

    query, _, pwd = url.path[1:].partition('?')
    pwd = url.query if not pwd else pwd
    pwd, _, channel = pwd.partition('#')
    channel = url.fragment if not channel else channel
    db = tuple((int(x) for x in query.split(',')))
    db = db[0] if 1 == len(db) else db
    if not pwd:
        if not with_channel:
            return ip, int(port), db
        return ip, int(port), db, channel

    pwd = pwd.partition('=')[-1]
    if not with_channel:
        return ip, int(port), db, pwd
    return ip, int(port), db, pwd, channel


def create_mg_con(mongo_url, use_slave=False):
    """创建数据库连接对象
    :param mongo_url: mongodb://<user>:<pass>@<ip>:<port>/<db>
    """
    # from pymongo import Connection
    from pymongo import MongoClient

    # con = Connection(mongo_url)
    conn = MongoClient(mongo_url)
    if use_slave:
        conn.slave_okay = True
    return conn


def create_mg_db(mongo_url, use_slave=False):
    """创建DB对象
    :param mongo_url: mongodb://<user>:<pass>@<ip>:<port>/<db>
    """
    con = create_mg_con(mongo_url, use_slave)
    return con[urlparse(mongo_url).path[1:]]


def mongo2utf8(d):
    if isinstance(d, unicode):
        return bs2utf8(d)
    elif isinstance(d, (list, tuple)):
        return [mongo2utf8(x) for x in d]
    elif isinstance(d, dict):
        ret = {}
        for k, v in d.items():
            if isinstance(k, unicode):
                k = bs2utf8(k)
            if isinstance(v, unicode):
                v = bs2utf8(v)
            elif isinstance(v, datetime):
                v = int(time.mktime(v.timetuple()))
            elif isinstance(v, (list, tuple)):
                v = [mongo2utf8(x) for x in v]
            elif isinstance(v, dict):
                v = mongo2utf8(v)

            ret[k] = v
        return ret
    else:
        return d


def pretty_unit(units, tot):
    """
    转换时间单位等
    """
    hit = None
    for p in units:
        _ = tot / p[1]
        if 0 != _:
            hit = 1
            yield '{0}{1}'.format(_, p[0])
            tot %= p[1]
    if not hit:
        yield '0{0}'.format(units[-1][0])


def iter_file(fn):
    """
    迭代文件行
    :param fn:
    """
    with open(fn) as fd:
        while 1:
            l = fd.readline()
            if not l:
                break
            l = l.strip()
            if not l:
                continue
            yield l
