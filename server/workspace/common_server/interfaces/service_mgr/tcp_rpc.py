#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-29

@author: Jay
"""
import ujson
from utils.crypto.sign import Signer
from utils.service_control.setting import RT_CPU_USAGE_RDM


def start_service(tcp_rpc_client, service_type, ip):
    params = {"service_type": service_type,
              "ip": ip}
    params['sign'] = Signer().gen_sign(**params)
    return ujson.loads(tcp_rpc_client.fetch_async("start_service", ujson.dumps(params)))


def stop_service(tcp_rpc_client, service_id):
    params = {"service_id": service_id}
    params['sign'] = Signer().gen_sign(**params)
    return ujson.loads(tcp_rpc_client.fetch_async("stop_service", ujson.dumps(params)))


def find_service(tcp_rpc_client, service_type, rdm_type=RT_CPU_USAGE_RDM, rdm_param=1):
    params = {"service_type": service_type,
              "rdm_type": rdm_type,
              "rdm_param": rdm_param}
    params['sign'] = Signer().gen_sign(**params)
    return ujson.loads(tcp_rpc_client.fetch_async("find_service", ujson.dumps(params)))

def find_services(tcp_rpc_client, service_type, rdm_type=RT_CPU_USAGE_RDM, rdm_param=1):
    params = {"service_type": service_type,
              "rdm_type": rdm_type,
              "rdm_param": rdm_param}
    if rdm_type != RT_CPU_USAGE_RDM:
        assert isinstance(rdm_param, list)
    params['sign'] = Signer().gen_sign(**params)
    return ujson.loads(tcp_rpc_client.fetch_async("find_services", ujson.dumps(params)))


def find_tp_service(tcp_rpc_client, service):
    params = {"service": service}
    params['sign'] = Signer().gen_sign(**params)
    return ujson.loads(tcp_rpc_client.fetch_async("find_tp_service", ujson.dumps(params)))

def view_logic_services(tcp_rpc_client, viewer, state=None):
    params = {"viewer": viewer,
              "state": state}
    params['sign'] = Signer().gen_sign(**params)
    return ujson.loads(tcp_rpc_client.fetch_async("view_logic_services", ujson.dumps(params)))

def view_tp_services(tcp_rpc_client, viewer):
    params = {"viewer": viewer}
    params['sign'] = Signer().gen_sign(**params)
    return ujson.loads(tcp_rpc_client.fetch_async("view_tp_services", ujson.dumps(params)))


def get_wc_clt_access_token(tcp_rpc_client):
    """
    获取微信客户端访问码
    :return: access_token
    """
    params = {}
    params['sign'] = Signer().gen_sign(**params)
    return ujson.loads(tcp_rpc_client.fetch_async("get_wc_clt_access_token", ujson.dumps(params)))

def get_wc_openid(tcp_rpc_client, code):
    """
    根据code获取微信用户openid
    :return: openid
    """
    params = {"code": code}
    params['sign'] = Signer().gen_sign(**params)
    return ujson.loads(tcp_rpc_client.fetch_async("get_wc_openid", ujson.dumps(params)))


def get_device_type(tcp_rpc_client, code=None):
    """
    获取设备类型列表
    :param tcp_rpc_client:
    :return:
    """
    params = {}
    if code:
        params['code'] = code
    params['sign'] = Signer().gen_sign(**params)
    return ujson.loads(tcp_rpc_client.fetch_async("get_device_type", ujson.dumps(params)))

def get_roster_m_ls(tcp_rpc_client):
    params = {}
    params['sign'] = Signer().gen_sign(**params)
    return ujson.loads(tcp_rpc_client.fetch_async('get_roster_m_ls', ujson.dumps(params)))

def get_roster_s_ls(tcp_rpc_client):
    params = {}
    params['sign'] = Signer().gen_sign(**params)
    return ujson.loads(tcp_rpc_client.fetch_async('get_roster_s_ls', ujson.dumps(params)))
