#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/7

@author: Jay
"""
import ujson
import urllib2
import random
from utils.crypto.beiqi_sign import append_url_sign_tk


def get_cls(server_ip, tk, app_secret, port=8300):
    url = 'http://{ip}:{port}/audio/cls'.format(ip=server_ip, port=port)
    url = append_url_sign_tk(url, tk, app_secret)
    return ujson.loads(urllib2.urlopen(urllib2.Request(url)).read())


def get_album(server_ip, tk, app_secret, cls_id, port=8300):
    url = "http://{ip}:{port}/audio/album?cls_id={cls_id}".format(ip=server_ip, port=port, cls_id=urllib2.quote(cls_id.encode('utf-8')))
    url = append_url_sign_tk(url, tk, app_secret)
    print url
    return ujson.loads(urllib2.urlopen(urllib2.Request(url)).read())


def get_list(server_ip, tk, app_secret, album_id, port=8300):
    url = 'http://{ip}:{port}/audio/list?album_id={album_id}'.format(ip=server_ip, port=port, album_id=album_id)
    url = append_url_sign_tk(url, tk, app_secret)
    return ujson.loads(urllib2.urlopen(urllib2.Request(url)).read())


def pub_2_dev(server_ip, tk, app_secret, sn, name, ref, port=8300):
    url = 'http://{ip}:{port}/audio/pub_2_dev?dev_sn={sn}&name={name}&ref={ref}'.format(
        ip=server_ip,
        port=port,
        sn=urllib2.quote(sn),
        name=urllib2.quote(name),
        ref=urllib2.quote(ref))
    url = append_url_sign_tk(url, tk, app_secret)
    return urllib2.urlopen(urllib2.Request(url)).read()


def get_rdm_list(server_ip, tk, app_secret, port=8300):
    cls_ls = get_cls(server_ip, tk, app_secret)
    print cls_ls
    select_cls = random.choice(cls_ls)['id']
    album_ls = get_album(server_ip, tk, app_secret,select_cls)
    print album_ls
    select_album = random.choice(album_ls)['id']

    url = 'http://{ip}:8300/audio/list?album_id={album_id}'.format(ip=server_ip, album_id=select_album)
    url = append_url_sign_tk(url, tk, app_secret)
    print url
    return ujson.loads(urllib2.urlopen(urllib2.Request(url)).read())


def chat_bcast(server_ip, tk, app_secret, file_type, fn, ref,  port=8300):
    url = 'http://{ip}:8300/chat/bcast?file_type={ftype}&fn={fn}&ref={ref}'.format(
        ip=server_ip,
        ftype=urllib2.quote(file_type),
        fn=urllib2.quote(fn),
        ref=urllib2.quote(ref))
    url = append_url_sign_tk(url, tk, app_secret)
    print url
    return urllib2.urlopen(urllib2.Request(url)).read()


def add_device(server_ip, tk, app_secret, code,  port=8300):
    url = 'http://{ip}:{port}/add_device?code={code}'.format(
        ip=server_ip,
        port=port,
        code=code)
    url = append_url_sign_tk(url, tk, app_secret)
    return urllib2.urlopen(urllib2.Request(url)).read()


def add_code(server_ip, tk, app_secret, code,  port=8300):
    url = 'http://{ip}:{port}/eticket/add?code={code}'.format(ip=server_ip, port=port, code=code)
    url = append_url_sign_tk(url, tk, app_secret)
    print url
    return ujson.loads(urllib2.urlopen(urllib2.Request(url)).read())


def check_code(server_ip, tk, app_secret, code,  port=8300):
    url = 'http://{ip}:{port}/eticket/check?code={code}'.format(ip=server_ip, port=port, code=code)
    url = append_url_sign_tk(url, tk, app_secret)
    return ujson.loads(urllib2.urlopen(urllib2.Request(url)).read())
