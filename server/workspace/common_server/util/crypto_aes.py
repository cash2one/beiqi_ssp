# coding:utf-8

from Crypto.Cipher import AES
import binascii
from convert import pad, unpad


def ecb_decrypt(text, key):
    """
    decrypt request message
    @param key: 服务器预先分配的20字节随机串，aes加密和hmac-sha1校验密钥相关
    @param text: 待解密的文本，前32字节为aes解密后的密文，后40字节为相关hmac-sha1校验值
    """
    if not key or not isinstance(key, str):
        return None
    if not text or not isinstance(text, str):
        return None
    
    text = binascii.unhexlify(text)  
    aes_after = AES.new(key, AES.MODE_ECB).decrypt(text)

    return unpad(aes_after)


def ecb_encrypt(text, key):
    """
    encrypt response message
    @param key: 用来AES（ECB模式）加密的密钥
    @param text: 待加密的字符串
    """   
    if not key or not isinstance(key, str):
        return None
    if not text or not isinstance(text, str):
        return None
    
    # 对明文做长度padding，必须为16的整数倍
    text = pad(text, 16)
    return binascii.hexlify(AES.new(key, AES.MODE_ECB).encrypt(text))


def encrypt(plain, key, iv, seg_size, seg_ratio = 3):
    """
    :param key: aes密钥
    :param iv: aes iv
    :param seg_size: aes段大小，为8的倍数，此处为24，一定程度上优化性能
    :param seg_ratio: 冗余参数，仅仅保证tornado设置不出错
    """
    assert plain and isinstance(plain, str)
    assert key and isinstance(key, str) and 16 == len(key)
    assert iv and isinstance(iv, str) and 16 == len(iv)
    assert seg_size and isinstance(seg_size, int)
    assert seg_ratio and isinstance(seg_ratio, int) \
        and 8 == seg_size / seg_ratio and 0 == seg_size % seg_ratio

    # padding
    plain = pad(plain, seg_ratio)
    return binascii.b2a_hex(AES.new(key, AES.MODE_CFB, iv, segment_size = seg_size).encrypt(plain))


def decrypt(s, key, iv, seg_size, seg_ratio = 3):
    """
    :param seg_ratio: aes密文的长度必定为ratio的整数倍
    """
    if not s or not isinstance(s, str):
        return None
    # 1->2 binascii, one seg_ratio
    if 0 != len(s) % (2 * seg_ratio):
        return None
    _ = AES.new(key, AES.MODE_CFB, iv, segment_size = seg_size).decrypt(binascii.a2b_hex(s))

    # unpadding
    return unpad(_)
