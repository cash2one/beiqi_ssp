#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-21

@author: Jay
"""
import ujson


def doc(http_rpc_client):
    url = "doc"
    return http_rpc_client.fetch_async(url)

def root(http_rpc_client):
    url = ""
    return http_rpc_client.fetch_async(url)

def services(http_rpc_client, service=""):
    url = "services?service=%s" % service
    return http_rpc_client.fetch_async(url)

def locate(http_rpc_client, service):
    url = "locate?service=%s" % service
    return ujson.loads(http_rpc_client.fetch_async(url))

def get_public_key(http_rpc_client):
    url = "get_public_key"
    return http_rpc_client.fetch_async(url)

def device_type(http_rpc_client):
    url = "http_rpc_client"
    return ujson.loads(http_rpc_client.fetch_async(url))

def service_doc(http_rpc_client, service):
    url = "service_doc?service=%s" % service
    return http_rpc_client.fetch_async(url)
