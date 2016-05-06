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
from utils.network.http import HttpRpcClient
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from utils.crypto.beiqi_sign import beiqi_tk_sign_wapper
from util.convert import bs2utf8
from util.sso.moments import add_comment, save_comment_info
from util.filetoken import gen_file_tk
from util.redis_cmds.wechat import get_wechat_access_token
from util.redis_cmds.circles import get_user_nickname
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.cloud_push_pack import pack as push_pack
from util.sso.moments import get_comment_file, del_comment_info, del_comment, del_share_info, del_share
from util.internal_forward.leveldb_encode import encode as level_encode
from util.sso.moments import add_like, cancel_like
from util.sso.moments import get_share_by_time, get_share_by_quantity, get_like, get_comment, retrieve_share_info, retrieve_comment_info
from util.redis_cmds.circles import get_dev_primary, get_group_primary, get_group_followers, get_sn_of_gid
from util.sso.moments import add_share, save_share_info, add_self_share
from util.sso.moments import del_one_comment
from setting import ssp_down_file_url, wechat_comment_page_url
from config import GDevRdsInts, GMQDispRdsInts, GAccRdsInts, GLevelDBClient


device_tbl = 'device_info'


@route(r'/comment')
class CommentHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def post(self, user_name, share_id, reply_to='', comment_id='', text='', type='', file=''):
        share_info = GDevRdsInts.execute([retrieve_share_info(share_id)])
        if share_info is None:
            return {'status': 1}

        comment_id_list = GDevRdsInts.execute([get_comment(share_id)])
        if comment_id != '' and comment_id not in comment_id_list:
            logger.debug('comment, comment_id={0}'.format(comment_id))
            return {'status': 2}

        now = str(time.time())
        new_comment_id = ':'.join(('comment', now, user_name))

        GDevRdsInts.pipe_execute((add_comment(share_id, new_comment_id), save_comment_info(share_id, new_comment_id, reply_to, comment_id, text, type, file)))

        accounts = [reply_to] if reply_to is not None else []
        accounts += [share_id.split(':')[-1]]
        like_list = GDevRdsInts.execute([get_like(share_id)])

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
                    pic_url =  ssp_down_file_url + urllib.urlencode({'tk': tk, 'r': ref})

                url = ""
                if not file:
                    url = wechat_comment_page_url + urllib.urlencode({'text': text})

                token = GAccRdsInts.execute([get_wechat_access_token()])
                customerServiceUrl = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=' + token
                nickname = GDevRdsInts.execute([get_user_nickname(user_name)])
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
                GMQDispRdsInts.execute(
                        [shortcut_mq(
                            'cloud_push',
                            # sourcer, cb, from, description
                            push_pack(user_name, 'comment', 2, ':'.join((user_name, share_id, reply_to, comment_id, text, type, file)), account=acc)
                        )]
                    )

        return {'comment_id': new_comment_id}


@route(r'/delete_comment')
class DeleteCommentHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def post(self, user_name, share_id, comment_id):
        if user_name != comment_id.split(':')[-1]:
            logger.debug('delete comment, acc=%r, share_id=%r, comment_id=%r' % (user_name, share_id, comment_id))
            return {'status': 1}

        fn = GDevRdsInts.execute([get_comment_file(share_id, comment_id)])
        if fn is not None:
            GLevelDBClient.forward(level_encode('delete', 0, fn))

        GDevRdsInts.pipe_execute((del_one_comment(share_id, comment_id), del_comment_info(share_id, comment_id)))
        return {'status': 0}


@route(r'/delete_share')
class DeleteShareHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def post(self, user_name, share_id):
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

        share_info = GDevRdsInts.execute([retrieve_share_info(share_id)])
        if share_info is None:
            return {'status': 2}

        files = share_info.get('files')
        if files:
            fns = json.loads(files)
            logger.debug(u'delete share, share_id={0}, gid={1}, fns={2}'.format(share_id, gid, fns))
            for k, v in fns.items():
                GLevelDBClient.forward(level_encode('delete', 0, bs2utf8(v)))

        comment_id_list = GDevRdsInts.execute([get_comment(share_id)])
        if comment_id_list is not None:
            for comment_id in comment_id_list:
                fn = GDevRdsInts.execute([get_comment_file(share_id, comment_id)])
                GLevelDBClient.forward(level_encode('delete', 0, fn))
                GDevRdsInts.execute([del_comment_info(share_id, comment_id)])

        GDevRdsInts.pipe_execute((del_share(user_name, share_id), del_comment(share_id), del_share_info(share_id)))

        if gid:
            sn = GDevRdsInts.execute([get_sn_of_gid(gid)])

            accounts = GDevRdsInts.execute([get_group_followers(gid)])
            primary_account = GDevRdsInts.execute([get_group_primary(gid)])
            accounts.add(primary_account)
            accounts.add(sn)

            logger.debug(u'accounts={0}'.format(accounts))
            for user in accounts:
                if user_name == user:
                    continue
                GDevRdsInts.execute([del_share(user, share_id)])
                GMQDispRdsInts.execute(
                    [shortcut_mq(
                        'cloud_push',
                        push_pack(user_name, 'delete_share', 2, share_id, account=user)
                    )]
                )

        return {'status': 0}

    def get_dev_primary_by_sn(self, dev_sn):
        logger.debug(u'DeleteShareHandler::get_dev_primary_by_gid, dev_sn={0}'.format(dev_sn))
        dev_primary = GDevRdsInts.execute([get_dev_primary(dev_sn)])
        if not dev_primary:
            sql = 'SELECT * FROM {0} WHERE sn = %s limit 1'.format(device_tbl)
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
        dev_sn = GDevRdsInts.execute([get_sn_of_gid(gid)])
        if self.is_device(del_acc):
            logger.debug(u'DeleteShareHandler::can_delete, is_device={0}'.format(del_acc))
            return del_acc == dev_sn
        # primary
        return self.get_dev_primary_by_sn(dev_sn) == del_acc


@route(r'/like')
class LikeHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def post(self, user_name, share_id, action):
        if action == 'add':
            GDevRdsInts.execute([add_like(share_id, user_name)])
        elif action == 'cancel':
            GDevRdsInts.execute([cancel_like(share_id, user_name)])
        else:
            return {'status': 1}
        return {'status': 0}


@route(r'/refresh_moments')
class RefreshMomentsHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def post(self, user_name, start=None, end=None, quantity=None, gids=None, pid='', user=''):
        logger.debug('refresh moments, start={0}, end={1}, acc={2}, quantity={3}'.format(start, end, user_name, quantity))
        if (user_name and (start or quantity)) is None:
            return {'status': 2}

        if quantity is not None:
            quantity = int(quantity)
            if quantity < 0:
                return {'status': 3}

            share_id_list = GDevRdsInts.execute([get_share_by_quantity(user_name, quantity)])
        else:
            start = float(start)
            if end is None:
                end = float('%0.2f' % time.time())
            else:
                end = float(end)

            share_id_list = GDevRdsInts.execute([get_share_by_time(user_name, start, end)])

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

            share_info = GDevRdsInts.execute([retrieve_share_info(share_id)])
            comment_id_list = GDevRdsInts.execute([get_comment(share_id)])
            like_list = GDevRdsInts.execute([get_like(share_id)])
            comment_info_list = {}
            for comment_id in comment_id_list:
                comment_info = GDevRdsInts.execute([retrieve_comment_info(share_id, comment_id)])
                comment_info_list[comment_id] = comment_info
            share_info['like_list'] = like_list
            share_info['comment_info_list'] = comment_info_list
            result[share_id] = share_info
        return result


@route(r'/share')
class RefreshMomentsHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def post(self, user_name, gid, share_to, location, text, type, files):
        primary_account = GDevRdsInts.execute([get_group_primary(gid)])
        if primary_account is None:
            return {'status': 1}

        ts = float('%0.2f' % time.time())
        share_id = ':'.join(('share', str(ts), gid, user_name))
        GDevRdsInts.execute([add_self_share(user_name, ts, share_id)])
        GDevRdsInts.execute([save_share_info(share_id, user_name, gid, share_to, location, text, type, files)])

        accounts = GDevRdsInts.execute([get_group_followers(gid)])
        logger.debug('share, accounts={0}'.format(accounts))
        # accounts is set object
        accounts.add(primary_account)
        sn = GDevRdsInts.execute([get_sn_of_gid(gid)])
        accounts.add(sn)

        logger.debug('share, accounts={0}'.format(accounts))

        for acc in accounts:
            GDevRdsInts.execute([add_share(acc, share_id, ts)])
            if acc == user_name:
                continue
            elif acc[:3] == 'wx#':
                continue
            GMQDispRdsInts.execute(
                    [shortcut_mq(
                        'cloud_push',
                        push_pack(user_name, 'share', 2, ':'.join((share_id, text, type, files)), account=acc)
                    )]
                )
        return {'share_id': share_id}


