# coding:utf-8

from Crypto.Hash import SHA, HMAC
from binascii import a2b_hex, b2a_hex
import random
import struct
import time

from util.convert import is_cdma_tid, is_imsi, take_offset_chars, is_gsm_tid, is_mobile, redis_encode_batch
from util.crypto_aes import encrypt, decrypt
from util.id_conv import rawid_tuple, tuple_rawid, parse_io_options
from util.oem_account_key import oem_accounts


# 所有工厂fid和server_key
ALL_FACTORY_KEY_LIST = 'factory'
# 所有新鲜设备
ALL_UNBOUND_DEVLIST = 'unbound'
# id->主帐号
PID_PRIMARY_ACCOUNT_MAP = 'devlist'
# 预先存储id与主帐号的关系
STUB_BOUND_DEVLIST = 'gen:dev:stub'
# 主帐号设备列表
PRIMARY_DEV_LIST = 'gen:dev:primary:owned'
# id对应所有子帐号列表
PID_SUB_ACCOUNT_SET = 'gen:dev:id:subaccounts'
# 子帐号关注列表
SUB_ACCOUNT_FOLLOWED_PID_LIST = 'gen:dev:subaccount:followed'
# id和imei的映射关系
FAC_PID_IMEI_IMSI_etc_MAPPING = 'gen:dev:id:imei:imsi'
ACCOUNT_ALIAS_MAPPING = 'gen:dev:id:account:alias'

CDMA_SMS_ID_IMSITID = 'gen:cdma:sms:id:imsi'


#设备INFO
DEV_INFO = 'gen:dev:info'


#用户信息流
FEED_PREFIX = 'res:feed'

QR_CRYPTO_KEY = '~\xa1D\xa5\xa4\xd5G\xf7\xbeR\t\\f*\xcb\xb7'
QR_CRYPTO_IV = '\xe1\xba\x90RC\xf0Cu\x8d\xceE\xfdz(\x00\x18'

# 设备lpm时间
DEV_LPM = 'gen:dev:lpm'


def get_factory_key(fid):
    assert fid and isinstance(fid, str)
    return 'hget', ALL_FACTORY_KEY_LIST, 'factory:{0}'.format(fid)


def gen_code(ptu_id, akey, aes_key, aes_iv, hmac_sha1_key='8d35ba51c374e0f9d263', aes_seg_size=24):
    """
    返回36字节QR码、移除io选项的新id，还有io选项
    由于AES加密转换ascii的关系，明文长度为36/2
    ptu_id(4) + akey(4) + offset(1) + hash(9)

    :param ptu_id: 8字节字符串
    :param akey: 4字节16进制或者8字节ascii码，产线生成
    :param hmac_sha1_key: hmac_sha1密钥
    """
    _ = rawid_tuple(ptu_id, with_io=True)
    if not _:
        return None

    _, typ, sn, io = _

    if not akey or not isinstance(akey, str) or len(akey) not in (4, 8):
        return None
    if 8 == len(akey):
        akey = a2b_hex(akey)
    if not hmac_sha1_key or not isinstance(hmac_sha1_key, str) or 20 != len(hmac_sha1_key):
        return None

    ptu_id = struct.pack('>I', tuple_rawid(io, typ, sn))
    assert 4 == len(ptu_id) and 4 == len(akey)

    digest = HMAC.new(hmac_sha1_key, ptu_id + akey, SHA).hexdigest()
    offset = random.randint(0, 39)
    return encrypt('{0}{1}{2}{3}'.format(ptu_id,
                                         akey,
                                         struct.pack('>B', offset),
                                         take_offset_chars(digest, offset, 9)), aes_key,
                   aes_iv, aes_seg_size), typ, sn, io


def extract(code, aes_key, aes_iv, hmac_sha1_key='8d35ba51c374e0f9d263'):
    if not code or not isinstance(code, str) or 36 != len(code):
        return None

    code = decrypt(code, aes_key, aes_iv, 24, 3)
    if not code:
        return None

    ptu_id = code[:4]
    akey = code[4:8]
    offset = struct.unpack('>B', code[8])[0]
    if take_offset_chars(HMAC.new(hmac_sha1_key, ptu_id + akey, SHA).hexdigest(), offset, 9) != code[9:]:
        return None
    return rawid_tuple(b2a_hex(ptu_id), True), b2a_hex(akey)


def test_dev_unbound(ptu_id):
    if not (ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)):
        raise ValueError('ptu_id:%s' % ptu_id)
    return 'hget', ALL_UNBOUND_DEVLIST, ptu_id


def test_dev_exist(ptu_id):
    """
    检查是否存在未绑定的设备以及是否已绑定过主帐号，由工厂接口发起
    注意unbound返回的akey包含了io选项，见 prestore_fac_devs 函数
    """
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    return ('hget', ALL_UNBOUND_DEVLIST, ptu_id), \
           ('hget', PID_PRIMARY_ACCOUNT_MAP, ptu_id)


def stub_dev_primaryaccount(ptu_id, akey, io, account):
    """
    预先存储pid和用户的关系
    """
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    assert akey and isinstance(akey, str) and 8 == len(akey)
    assert isinstance(io, int) and 0 <= io <= 0b111
    assert account and isinstance(account, str)

    key = ':'.join((STUB_BOUND_DEVLIST, ptu_id))
    return (('set', key, '{0}:{1}:{2}'.format(io, akey, account)),
            ('expire', key, 300))


def get_stubed_dev_primaryaccount(ptu_id):
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    return 'get', ':'.join((STUB_BOUND_DEVLIST, ptu_id))


def clear_stubed_dev_primaryaccount(ptu_id):
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    return 'delete', ':'.join((STUB_BOUND_DEVLIST, ptu_id))


def connect_dev_primaryaccount(pid, akey, io, account):
    """
    连接设备和主帐号

    :param pid: 8字节字符串，仅在mysql中存储整型
    :param akey: 设备akey
    :param io: io选项
    :param account: 用户帐号
    """
    assert pid and isinstance(pid, str) and 8 == len(pid)
    assert akey and isinstance(akey, str) and 8 == len(akey)
    assert isinstance(io, int) and 0 <= io <= 0b111
    assert account and isinstance(account, str)

    return ('hdel', ALL_UNBOUND_DEVLIST, pid), \
           ('hsetnx', PID_PRIMARY_ACCOUNT_MAP, pid, '{0}:{1}:{2}'.format(io, akey, account)), \
           ('sadd', ':'.join((PRIMARY_DEV_LIST, account)), pid)


def set_alias(ptu_id, account, alias):
    """
    设置pid与帐号的别名
    """
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    assert account and isinstance(account, str)
    assert alias and isinstance(alias, str) and len(alias) <= 15

    return 'hset', ':'.join((ACCOUNT_ALIAS_MAPPING, ptu_id)), account, alias


def get_alias(ptu_id, account):
    """
    获取pid与帐号的别名
    """
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    assert account and isinstance(account, str)

    return 'hget', ':'.join((ACCOUNT_ALIAS_MAPPING, ptu_id)), account


def get_all_alias(ptu_id):
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    return 'hgetall', ':'.join((ACCOUNT_ALIAS_MAPPING, ptu_id))


def unlink_alias(ptu_id, account):
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    assert account and isinstance(account, str)
    return 'hdel', ':'.join((ACCOUNT_ALIAS_MAPPING, ptu_id)), account


def drop_aliases(ptu_id):
    """
    删除所有别名
    :param ptu_id: 设备id
    """
    if not (ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)):
        raise ValueError('pid invalid: {0}'.format(ptu_id))
    return 'delete', ':'.join((ACCOUNT_ALIAS_MAPPING, ptu_id))


def append_dev_subaccount(ptu_id, sub_account):
    """
    关联设备与子帐号
    """
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    assert sub_account and isinstance(sub_account, str)
    return (('sadd', ':'.join((PID_SUB_ACCOUNT_SET, ptu_id)), sub_account),
            ('sadd', ':'.join((SUB_ACCOUNT_FOLLOWED_PID_LIST, sub_account)), ptu_id))


def is_dev_subaccounted(ptu_id, sub_account):
    """
    设备是否为子帐号所关注
    """
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    assert sub_account and isinstance(sub_account, str)

    return 'sismember', ':'.join((PID_SUB_ACCOUNT_SET, ptu_id)), sub_account


def list_dev_subaccounts(ptu_id):
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    return 'smembers', ':'.join((PID_SUB_ACCOUNT_SET, ptu_id))


def count_dev_subaccounts(ptu_id):
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    return 'scard', ':'.join((PID_SUB_ACCOUNT_SET, ptu_id))


def clear_subacc_follow(ptu_id, sub_acc):
    """
    清理子帐号关注关系
    :param ptu_id: 设备id
    :param sub_acc: 子帐号
    """
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    assert sub_acc and isinstance(sub_acc, str)

    return ('srem', ':'.join((PID_SUB_ACCOUNT_SET, ptu_id)), sub_acc), \
           ('srem', ':'.join((SUB_ACCOUNT_FOLLOWED_PID_LIST, sub_acc)), ptu_id)


def clear_all_dev_followed(pid, sub_accounts):
    """
    清理关注关系
    :param pid: 设备id
    :param sub_accounts: 子帐号
    """
    assert pid and isinstance(pid, str) and 8 == len(pid)
    yield 'delete', ':'.join((PID_SUB_ACCOUNT_SET, pid))
    if not sub_accounts:
        return
    for sub_acc in sub_accounts:
        yield 'srem', ':'.join((SUB_ACCOUNT_FOLLOWED_PID_LIST, sub_acc)), pid


def disconnect_dev_primaryaccount(ptu_id, akey, prior_account, io):
    """
    断开设备和主帐号
    :param akey: 设备akey
    :param prior_account: 之前的绑定用户
    """
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    assert akey and isinstance(akey, str)
    assert isinstance(io, int) and io <= 0b111

    return ('hdel', PID_PRIMARY_ACCOUNT_MAP, ptu_id), \
           ('hsetnx', ALL_UNBOUND_DEVLIST, ptu_id, '{0}:{1}'.format(akey, io)), \
           ('srem', ':'.join((PRIMARY_DEV_LIST, prior_account)), ptu_id)


def test_primary_bound(ptu_id):
    """
    测试是否被主帐号绑定
    """
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    return 'hget', PID_PRIMARY_ACCOUNT_MAP, ptu_id


def test_id_owned(primary_account, ptu_id):
    """
    测试设备是否被主帐号所有
    """
    assert primary_account and isinstance(primary_account, str)
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)

    return 'sismember', ':'.join((PRIMARY_DEV_LIST, primary_account)), ptu_id


def list_primary_devices(primary_account):
    """
    枚举主帐号设备
    """
    assert primary_account and isinstance(primary_account, str)
    return 'smembers', ':'.join((PRIMARY_DEV_LIST, primary_account))


def list_sub_devices(sub_account):
    """
    枚举子帐号设备
    :param sub_account: 子帐号
    """
    assert sub_account and isinstance(sub_account, str)
    return 'smembers', ':'.join((SUB_ACCOUNT_FOLLOWED_PID_LIST, sub_account))


def prestore_fac_devs(ptu_id, akey, io, p=None):
    """
    工厂预置设备id和akey

    注意：
    * imei仅gsm+wcdma设备才具备，虽然高德接口查询cdma基站也需要imei号，但此时imei无意义，随便填都可以
    * imsi适用于所有SP
    * cdma_tid仅用于电信物联平台注册
    """
    p = p or {}
    opt_data, opt_sms, opt_bt = parse_io_options(io)
    yield 'hsetnx', ALL_UNBOUND_DEVLIST, ptu_id, '{0}:{1}'.format(akey, io)
    if opt_sms:
        yield 'hsetnx', FAC_PID_IMEI_IMSI_etc_MAPPING, ptu_id, ':'.join((
            str(p.get(k, ''))
            for k in ('mcc', 'mnc', 'imei', 'imsi', 'cdma_tid')))
    area_code = str(p.get('area_code') or '')
    if area_code:
        yield 'setnx', ':'.join((GSM_AREA_CODE, ptu_id)), ':'.join((p.get('cdma_tid', ''), area_code))


def get_dev_imeiimsi_etc(ptu_id):
    """
    通过ptu_id获取imei&imsi
    """
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    return 'hget', FAC_PID_IMEI_IMSI_etc_MAPPING, ptu_id


def set_dev_imeiimsi_etc(ptu_id, v):
    """
    通过ptu_id设置imei&imsi
    """
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    return 'hset', FAC_PID_IMEI_IMSI_etc_MAPPING, ptu_id, v


def active_dev_sms(pid, sms_offsets):
    if not (pid and isinstance(pid, str) and 8 == len(pid)):
        raise ValueError('pid: %s' % pid)
    if not (sms_offsets and isinstance(sms_offsets, str) and 2 == len(sms_offsets)):
        raise ValueError('sms_offsets: %s' % sms_offsets)
    return 'hset', CDMA_SMS_ID_IMSITID, pid, sms_offsets


def get_dev_auth_offset(pid):
    assert pid and isinstance(pid, str) and 8 == len(pid)
    return 'hget', CDMA_SMS_ID_IMSITID, pid


def set_dev_info(ptu_id, info_str):
    """
    设置设备版本信息等
    由外部编码
    """
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)
    assert info_str and isinstance(info_str, str)

    return 'hset', DEV_INFO, ptu_id, info_str


def get_dev_info(ptu_id):
    assert ptu_id and isinstance(ptu_id, str) and 8 == len(ptu_id)

    return 'hget', DEV_INFO, ptu_id


