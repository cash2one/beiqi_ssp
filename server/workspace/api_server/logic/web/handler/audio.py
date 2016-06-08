#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/2

@author: Jay
"""
import urllib
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.cloud_push_pack import pack as push_pack
from util.convert import bs2utf8
from config import GMQDispRdsInts
from utils.crypto.beiqi_sign import beiqi_tk_sign_wapper
from db.db_oper import DBBeiqiSspInst
from setting import DB_TBL_RES_CLS, DB_TBL_RES_ALBUM, DB_TBL_RESOURCE, PAGE_COUNT


@route(r'/audio/cls')
class AudioClsHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, user_name):
        sql = "SELECT * FROM {tbl}".format(tbl=DB_TBL_RES_CLS)
        logger.debug('AudioClsHandler::user=%r, sql=%r' % (user_name, sql))
        ret_list = DBBeiqiSspInst.query(sql)
        return ret_list


@route(r'/audio/album')
class AudioAlbumHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, user_name, cls_id):
        sql = "SELECT * FROM {tbl} WHERE cls_id = '{cls_id}'".format(tbl=DB_TBL_RES_ALBUM, cls_id=cls_id)
        logger.debug('AudioAlbumHandler::user=%r, sql=%r' % (user_name, sql))
        ret_list = DBBeiqiSspInst.query(sql)
        return ret_list


@route(r'/audio/list')
class AudioListHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, user_name, album_id, page_idx=1):
        sql = "SELECT * FROM {tbl} WHERE album_id = '{album_id}' limit {start},{end}"\
            .format(tbl=DB_TBL_RESOURCE,
                    album_id=album_id,
                    start=PAGE_COUNT * (page_idx - 1),
                    end=PAGE_COUNT)
        logger.debug('AudioListHandler::user=%r, sql=%r' % (user_name, sql))
        ret_list = DBBeiqiSspInst.query(sql)
        return ret_list


@route(r'/audio/pub_2_dev')
class AudioPub2DevHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, user_name, dev_sn, name, ref):
        logic = "play"
        type = "audio"
        payload = ':'.join([bs2utf8(urllib.quote_plus(v)) for v in (logic, type, name, ref)])

        GMQDispRdsInts.send_cmd(*
            shortcut_mq('dev_msg',
                        push_pack(user_name, 'msg', 2, payload, account=dev_sn)
                        )
        )
