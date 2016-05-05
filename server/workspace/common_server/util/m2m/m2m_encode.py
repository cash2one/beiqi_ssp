#coding: utf-8

import binascii
from util.bit import encode_bits, decode_bits

_PROTOCOL_VER = '0100'
_HEAD_LEN = 20
_HASH_LEN = 6

#register body
_ESN = '00000000'           #8bytes
_MEID = '00000000000000'    #14bytes
_UIMID = '0000'             #4bytes
_BSID = '000000'            #6bytes

_command_id = {
    'REGISTER':     0x0003,
    'REGISTER_RSP': 0x8003
}

_tag = {
    'CRC':              0x0003,
    'ModuleVendor':     0x2006,
    'ModuleType':       0x2007,
    'TermSoftVersion':  0x2008
}

_crc_table = []

def _build_crc_table():
    for i in range(256):
        value = i << 8
        accum = 0
        for j in range(8):
            if (value ^ accum) & 0x8000:
                accum = (accum << 1) ^ 0x1021
            else:
                accum <<= 1
            value <<= 1

        _crc_table.append(accum)

_build_crc_table()
        
def _calc_crc_16(data):
    accum = 0
    for i in range(len(data)):
        v = ord(data[i])
        accum = (accum << 8) ^ (_crc_table[(accum >> 8) ^ v] & 0xffff)
        accum = accum & 0xffff

    return accum


def m2m_register_req_encode(seq, termID, imsi, vendor, typ, version):
    """
    request:
        head + body + crc
    head:
        Command_Length: 2bytes
        Protocol_Version: 2bytes
        Command_ID: 2bytes
        Sequence_No: 2bytes, 0~0xffff
        Terminal_No: 10bytes
        Head_Reserve: 2bytes

    body: 
        定长部分:
        ESN: 8bytes, 全0
        MEID: 14bytes, 全0
        IMSI: 15bytes
        UIMID: 4bytes, 全0
        BSID: 6bytes, 终端所处当前接入基站号(SID+NID+Base Station ID), 目前为全0
        RegisterReasonCode: 1bytes, 1表示新注册, 2表示换卡注册, 目前只支持新注册
        ComProtocol: 1bytes, 终端接入协议, 1表示1X协议

        TLV部分: Tag(2bytes) + Length(2bytes) + Value
        ModuleVendor: 生产厂商
        ModuleType: 型号
        TermSoftVersion:终端软件版本

    crc: TLV格式, 共6bytes
        crc: 2bytes

    """
    reason_code = 1  #新注册
    com_protocol = 1 #1X协议
    body_cons = _ESN + _MEID + imsi + _UIMID + _BSID + encode_bits(reason_code, 1) + encode_bits(com_protocol, 1)

    tlv_vendor = encode_bits(_tag.get('ModuleVendor'), 2) + encode_bits(len(vendor), 2) + vendor
    tlv_typ = encode_bits(_tag.get('ModuleType'), 2) + encode_bits(len(typ), 2) + typ 
    tlv_version = encode_bits(_tag.get('TermSoftVersion'), 2) + encode_bits(len(version), 2) + version 

    body = body_cons + tlv_vendor + tlv_typ + tlv_version
    
    command_length = _HEAD_LEN + len(body) +_HASH_LEN 
    command_id = _command_id.get('REGISTER')
    reserve = '00'
    
    head = encode_bits(command_length, 2) 
    head += binascii.a2b_hex(_PROTOCOL_VER)
    head += encode_bits(command_id, 2)
    head += encode_bits(seq, 2) 
    head += binascii.a2b_hex(termID) 
    head += reserve

    crc = _calc_crc_16(head + body)
    tlv_crc = encode_bits(_tag.get('CRC'), 2) + encode_bits(2, 2) + encode_bits(crc, 2)
    req = head + body + tlv_crc
    return req


def m2m_register_rsp_decode(response):
    """
    response:
        head + body

    head: 同request
    body:
        ResultCode: 1bytes, 0表示成功，其它为失败
    """
    seq = decode_bits(response[6:8], 2)
    body = response[_HEAD_LEN:]
    result_code = decode_bits(body[:1], 1)

    return seq, result_code
