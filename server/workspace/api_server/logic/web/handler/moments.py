#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/4

@author: Jay
"""
import ujson
import urllib
import json
import time
import urllib2
from utils.network.http import HttpRpcClient
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from utils.crypto.beiqi_sign import client_sign_wapper
from util.convert import bs2utf8, combine_redis_cmds
from util.sso.moments import add_comment, save_comment_info
from util.filetoken import gen_file_tk
from util.wechat import gen_wechat_access_token
from util.redis_cmds.circles import get_user_nickname
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.cloud_push_pack import pack as push_pack
from util.sso.moments import get_comment_file, del_comment_info, del_comment, del_share_info, del_share
from util.sso.moments import add_like, cancel_like
from util.sso.moments import get_share_by_time, get_share_by_quantity, get_like, get_comment, retrieve_share_info, retrieve_comment_info
from util.redis_cmds.circles import get_dev_primary, get_group_primary, get_group_followers, get_sn_of_gid
from util.sso.moments import add_share, save_share_info, add_self_share
from util.sso.moments import del_one_comment
from setting import BEIQI_FILE_DOWN_URL, WECHAT_COMMENT_PAGE_URL, DB_TBL_DEVICE_INFO, BEIQI_FILE_DELETE_URL
from config import GDevRdsInts, GMQDispRdsInts, GAccRdsInts


@route(r'/comment')
class CommentHandler(HttpRpcHandler):
    @web_adaptor()
    @client_sign_wapper()
    def post(self, user_name, share_id, reply_to='', comment_id='', text='', type='', file='', *args, **kwargs):
        share_info = GDevRdsInts.send_cmd(*retrieve_share_info(share_id))
        if share_info is None:
            return {'status': 1}

        comment_id_list = GDevRdsInts.send_cmd(*get_comment(share_id))
        if comment_id != '' and comment_id not in comment_id_list:
            logger.debug('comment, comment_id={0}'.format(comment_id))
            return {'status': 2}

        now = str(time.time())
        new_comment_id = ':'.join(('comment', now, user_name))

        GDevRdsInts.send_multi_cmd(*combine_redis_cmds(add_comment(share_id, new_comment_id), save_comment_info(share_id, new_comment_id, reply_to, comment_id, text, type, file)))

        accounts = [reply_to] if reply_to is not None else []
        accounts += [share_id.split(':')[-1]]
        like_list = GDevRdsInts.send_cmd(*get_like(share_id))

        accounts += like_list

        for acc in accounts:
            if acc[:3] == 'wx#':
                files = json.loads(share_info.get('files'))
                fn, ref = files.popitem()
                fn = bs2utf8(fn)
                ref = bs2utf8(ref)
                logger.debug('files = %r, fn = %r, ref = %r', files, fn, ref)

                tk = gen_file_tk(acc, fn, 0, 0)
                if fn[-4:] == '.jpg':
                    pic_url =  BEIQI_FILE_DOWN_URL + urllib.urlencode({'tk': tk, 'r': ref})

                url = ""
                if not file:
                    url = WECHAT_COMMENT_PAGE_URL + urllib.urlencode({'text': text})

                token = gen_wechat_access_token(GAccRdsInts)
                customerServiceUrl = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=' + token
                nickname = GDevRdsInts.send_cmd(*get_user_nickname(user_name))
                payload = {
                    "touser": acc[3:],
                    "msgtype": "news",
                    "news": {
                        "articles": [
                            {
                                "title": nickname + "评论了你的回复",
                                "description": text,
                                "url": url,
                                "picurl": pic_url
                            }
                        ]
                    }
                }
                logger.debug('pic_url = %r', pic_url)
                resp = HttpRpcClient().fetch_async(url=customerServiceUrl, body=ujson.dumps(payload, ensure_ascii=False))
                logger.debug('custom service send. resp = %r, payload = %r', resp.body, payload)

            else:
                GMQDispRdsInts.send_cmd(
                        *shortcut_mq(
                            'cloud_push',
                            # sourcer, cb, from, description
                            push_pack(user_name, 'comment', 2, ':'.join((user_name, share_id, reply_to, comment_id, text, type, file)), account=acc)
                        )
                    )

        return {'comment_id': new_comment_id}


@route(r'/delete_comment')
class DeleteCommentHandler(HttpRpcHandler):
    @web_adaptor()
    @client_sign_wapper()
    def post(self, user_name, share_id, comment_id, *args, **kwargs):
        if user_name != comment_id.split(':')[-1]:
            logger.debug('delete comment, acc=%r, share_id=%r, comment_id=%r' % (user_name, share_id, comment_id))
            return {'status': 1}

        fn = GDevRdsInts.send_cmd(*get_comment_file(share_id, comment_id))
        if fn is not None:
            urllib2.urlopen(BEIQI_FILE_DELETE_URL.format(file=fn))



        GDevRdsInts.send_multi_cmd(*combine_redis_cmds(del_one_comment(share_id, comment_id), del_comment_info(share_id, comment_id)))
        return {'status': 0}


@route(r'/delete_share')
class DeleteShareHandler(HttpRpcHandler):
    @web_adaptor()
    @client_sign_wapper()
    def post(self, user_name, share_id, *args, **kwargs):
        gid = ''
        sl = share_id.split(':')
        author = ''
        if len(sl) == 4:
            _, _, gid, author = sl
        elif len(sl) == 3:
            _, _, author = sl

        logger.debug(u'delete share, gid={0}, author={1}, acc={2}'.format(gid, author, user_name))

        if not self.can_delete(gid, author, user_name):
            return {'status': 1}

        share_info = GDevRdsInts.send_cmd(*retrieve_share_info(share_id))
        if share_info is None:
            return {'status': 2}

        files = share_info.get('files')
        if files:
            fns = json.loads(files)
            logger.debug(u'delete share, share_id={0}, gid={1}, fns={2}'.format(share_id, gid, fns))
            for k, v in fns.items():
                urllib2.urlopen(BEIQI_FILE_DELETE_URL.format(file=bs2utf8(v)))

        comment_id_list = GDevRdsInts.send_cmd(*get_comment(share_id))
        if comment_id_list is not None:
            for comment_id in comment_id_list:
                fn = GDevRdsInts.send_cmd(*get_comment_file(share_id, comment_id))
                urllib2.urlopen(BEIQI_FILE_DELETE_URL.format(file=fn))
                GDevRdsInts.send_cmd(*del_comment_info(share_id, comment_id))

        GDevRdsInts.send_multi_cmd(*combine_redis_cmds(del_share(user_name, share_id), del_comment(share_id), del_share_info(share_id)))

        if gid:
            sn = GDevRdsInts.send_cmd(*get_sn_of_gid(gid))

            accounts = GDevRdsInts.send_cmd(*get_group_followers(gid))
            primary_account = GDevRdsInts.send_cmd(*get_group_primary(gid))
            accounts.add(primary_account)
            accounts.add(sn)

            logger.debug(u'accounts={0}'.format(accounts))
            for user in accounts:
                if user_name == user:
                    continue
                GDevRdsInts.send_cmd(*del_share(user, share_id))
                GMQDispRdsInts.send_cmd(
                    *shortcut_mq(
                        'cloud_push',
                        push_pack(user_name, 'delete_share', 2, share_id, account=user)
                    )
                )

        return {'status': 0}

    def get_dev_primary_by_sn(self, dev_sn):
        logger.debug(u'DeleteShareHandler::get_dev_primary_by_gid, dev_sn={0}'.format(dev_sn))
        dev_primary = GDevRdsInts.send_cmd(*get_dev_primary(dev_sn))
        if not dev_primary:
            sql = 'SELECT * FROM {0} WHERE sn = %s limit 1'.format(DB_TBL_DEVICE_INFO)
            dev_ls = self.settings.get('mysql_db').query(sql, dev_sn)
            dev_primary = dev_ls[0].get('primary')
        logger.debug(u'DeleteShareHandler::get_dev_primary_by_gid, dev_primary={0}'.format(dev_primary))
        return dev_primary

    def is_device(self, acc):
        return "@" not in acc

    def can_delete(self, gid, author_acc, del_acc):
        # owner
        if author_acc == del_acc:
            return True

        # device
        dev_sn = GDevRdsInts.send_cmd(*get_sn_of_gid(gid))
        if self.is_device(del_acc):
            logger.debug(u'DeleteShareHandler::can_delete, is_device={0}'.format(del_acc))
            return del_acc == dev_sn
        # primary
        return self.get_dev_primary_by_sn(dev_sn) == del_acc


@route(r'/like')
class LikeHandler(HttpRpcHandler):
    @web_adaptor()
    @client_sign_wapper()
    def post(self, user_name, share_id, action, *args, **kwargs):
        if action == 'add':
            GDevRdsInts.send_cmd(*add_like(share_id, user_name))
        elif action == 'cancel':
            GDevRdsInts.send_cmd(*cancel_like(share_id, user_name))
        else:
            return {'status': 1}
        return {'status': 0}


@route(r'/refresh_moments')
class RefreshMomentsHandler(HttpRpcHandler):
    @web_adaptor()
    @client_sign_wapper()
    def post(self, user_name, start=None, end=None, quantity=None, gids=None, pid='', user='', *args, **kwargs):
        logger.debug('refresh moments, start={0}, end={1}, acc={2}, quantity={3}'.format(start, end, user_name, quantity))
        if (user_name and (start or quantity)) is None:
            return {'status': 2}

        if quantity is not None:
            quantity = int(quantity)
            if quantity < 0:
                return {'status': 3}

            share_id_list = GDevRdsInts.send_cmd(*get_share_by_quantity(user_name, quantity))
        else:
            start = float(start)
            if end is None:
                end = float('%0.2f' % time.time())
            else:
                end = float(end)

            share_id_list = GDevRdsInts.send_cmd(*get_share_by_time(user_name, start, end))

        if share_id_list is None or len(share_id_list) == 0:
            return {'status': 1}

        gids = gids.split(',') if gids else gids

        result = {}
        for share_id in share_id_list:
            if gids:
                gid = ''
                sl = share_id.split(':')
                if len(sl) == 4:
                    _, _, gid, author = sl
                elif len(sl) == 3:
                    _, _, author = sl

                if gid and gid not in gids:
                    continue

            share_info = GDevRdsInts.send_cmd(*retrieve_share_info(share_id))
            comment_id_list = GDevRdsInts.send_cmd(*get_comment(share_id))
            like_list = GDevRdsInts.send_cmd(*get_like(share_id))
            comment_info_list = {}
            for comment_id in comment_id_list:
                comment_info = GDevRdsInts.send_cmd(*retrieve_comment_info(share_id, comment_id))
                comment_info_list[comment_id] = comment_info
            share_info['like_list'] = like_list
            share_info['comment_info_list'] = comment_info_list
            result[share_id] = share_info
        return result


@route(r'/share')
class RefreshMomentsHandler(HttpRpcHandler):
    @web_adaptor()
    @client_sign_wapper()
    def post(self, user_name, gid, share_to, location, text, type, files, *args, **kwargs):
        primary_account = GDevRdsInts.send_cmd(*get_group_primary(gid))
        if primary_account is None:
            return {'status': 1}

        ts = float('%0.2f' % time.time())
        share_id = ':'.join(('share', str(ts), gid, user_name))
        GDevRdsInts.send_cmd(*add_self_share(user_name, ts, share_id))
        GDevRdsInts.send_cmd(*save_share_info(share_id, user_name, gid, share_to, location, text, type, files))

        accounts = GDevRdsInts.send_cmd(*get_group_followers(gid))
        logger.debug('share, accounts={0}'.format(accounts))
        # accounts is set object
        accounts.add(primary_account)
        sn = GDevRdsInts.send_cmd(*get_sn_of_gid(gid))
        accounts.add(sn)

        logger.debug('share, accounts={0}'.format(accounts))

        for acc in accounts:
            GDevRdsInts.send_cmd(*add_share(acc, share_id, ts))
            if acc == user_name:
                continue
            elif acc[:3] == 'wx#':
                continue
            GMQDispRdsInts.send_cmd(
                    *shortcut_mq(
                        'cloud_push',
                        push_pack(user_name, 'share', 2, ':'.join((share_id, text, type, files)), account=acc)
                    )
                )
        return {'share_id': share_id}


