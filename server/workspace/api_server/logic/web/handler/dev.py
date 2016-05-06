#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/4

@author: Jay
"""
import ujson
from utils import logger
from utils.route import route
from utils.network.http import HttpRpcHandler
from utils.wapper.web import web_adaptor
from utils.crypto.beiqi_sign import beiqi_tk_sign_wapper
from utils.network.http import HttpRpcClient
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.cloud_push_pack import pack as push_pack
from util.redis_cmds.circles import *
from util.redis_cmds.user_info import *
from util.redis_cmds.wechat import *
from util.redis_cmds.letters import *
from util.mq_packs.mysql_pack import pack as mysql_pack
from util.sso.moments import del_all_self_share
from util.sso.account import exist_account, set_account_pwd
from config import GDevRdsInts, GMQDispRdsInts, GAccRdsInts
from db.db_oper import DBBeiqiSspInst


dev_tbl = 'device_info'
pidinfo_tbl_name = 'gid_info'


@route(r'/dev/check_dev_args', name='/dev/check_dev_args')
class CheckDevArgsHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, user_name, sn):
        sql = 'SELECT 1 FROM {0} WHERE sn = %s'.format(dev_tbl)
        ret_list = DBBeiqiSspInst.query(sql, sn)
        if len(ret_list) == 0:
            return {'status': 1}

        primary = GDevRdsInts.execute([get_dev_primary(sn)])
        if primary is None:
            return {'status': 1}

        logger.debug('check dev args: pid: {0}, acc: {1}'.format(sn, user_name))

        GMQDispRdsInts.execute([
            shortcut_mq('cloud_push',
                        push_pack(user_name, 'check_dev_args', 2, '', account=sn)
                        )]
        )
        return {'status': 0}


@route(r'/dev/change_dev_args')
class ChangeDevArgsHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def post(self, user_name, sn, payload):
        logger.debug('change dev args: sn: {0}, payload: {1}, acc: {2}'.format(sn, payload, user_name))
        if not user_name or not sn or not payload:
            self.send_error(400)
            return

        sql = 'SELECT 1 FROM {0} WHERE sn = %s'.format(dev_tbl)
        ret_list = DBBeiqiSspInst.query(sql, sn)
        if len(ret_list) == 0:
            return {'status': 1}

        primary = GDevRdsInts.execute([get_dev_primary(sn)])
        if primary is None:
            return {'status': 1}

        GMQDispRdsInts.execute([
            shortcut_mq(
                'cloud_push',
                push_pack(user_name, 'change_dev_args', 2, payload, account=sn)
            )]
        )
        logger.debug('cloud_push doing')

        return {'state': 0}


@route(r'/dev/dev_ctrl')
class DevCtrlHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, user_name, sn, action):
        primary = GDevRdsInts.execute([get_dev_primary(sn)])
        if not primary:
            return {'state': 1}

        logger.debug('dev ctrl sn: {0}, action: {1}, acc: {2}'.format(sn, action, user_name))
        GMQDispRdsInts.execute([
            shortcut_mq(
                'cloud_push',
                push_pack(user_name, 'dev_ctrl', 2, action, account=sn)
            )]
        )
        return {'state': 0}


@route(r'/dev/dispatch_conf')
class DispatchConfHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, sn, saved_time):
        primary = GDevRdsInts.execute([get_dev_primary(sn)])
        if not primary:
            return {'state': 1}

        logger.debug('dispatch conf pid: {0}, saved_time: {1}, lvl result: {2}'.format(sn, saved_time, 'none'))
        return {'state': 0}


@route(r'/follow_review')
class FollowReviewHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, user_name, applicant, gid, allowed, msg=''):
        primary = GDevRdsInts.execute([get_group_primary(gid)])
        if not primary:
            return {'status': 1}

        if primary != user_name:
            return {'status': 2}

        sn = GDevRdsInts.execute([get_sn_of_gid(gid)])
        if allowed:
            GDevRdsInts.pipe_execute(follow_group(gid, sn, applicant))
            if applicant[:3] == 'wx#':
                # applicant from wechat
                logger.debug(u'wechat user follow: ', applicant)
                GDevRdsInts.execute([hset_wechat_gid(applicant, gid)])
                token = GAccRdsInts.execute([get_wechat_access_token()])
                customerServiceUrl = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=' + token
                payload = \
                {
                    "touser": applicant[3:],
                    "msgtype": "text",
                    "text":
                        {
                            "content": "恭喜你设备添加成功。可以给平板发送照片了！"
                        }
                }
                resp = HttpRpcClient().fetch_async(url=customerServiceUrl, body=ujson.dumps(payload, ensure_ascii=False))
                logger.debug('wechat resp.code = %r, body = %r', resp.code, resp.body)
                return {'status': 0}

        payload = ujson.dumps({'reviewer': user_name, 'allowed': allowed, 'msg': msg, 'gid': gid})
        logger.debug(u'follow review, applicant=%r, payload=%r' % (applicant, payload))
        # 把关注验证结果放到申请人的消息列表里
        GDevRdsInts.pipe_execute(set_user_group_msglist(applicant, gid, 'follow_review', payload))

        GMQDispRdsInts.execute(
            [shortcut_mq(
                'cloud_push',
                push_pack(user_name, 'follow_review', 2, payload, account=applicant)
            )]
        )
        return {'status': 0}


@route(r'/add_device')
class AddDeviceHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def post(self, user_name, code, msg='', file=''):
        if len(code) == 6:
            primary = GDevRdsInts.execute([get_group_primary(code)])
            if not primary:
                return {'status': 3}

            if user_name == primary:
                return {'status': 9}

            following = GDevRdsInts.execute([test_user_follow_group(user_name, code)])
            if following:
                return {'status': 8}

            payload = ujson.dumps({'applicant': user_name, 'pid': code, 'msg': msg, 'file': file, 'time': str(time.time())})

            # put follow request into primary msglist
            GMQDispRdsInts.pipe_execute(set_user_group_msglist(primary, code, 'follow', payload))

            GMQDispRdsInts.execute(
                [shortcut_mq(
                    'cloud_push',
                    push_pack(user_name, 'follow', 2, payload, account=primary))]
            )
            logger.debug('follow, acc={0}, followee={1}, msg={2}, file={3}'.format(user_name, code, msg, file))
            return {'status': 1}

        elif len(code) == 9:
            # 识别码, 绑定
            sn = GDevRdsInts.execute([get_ic_sn(code)])
            if not sn:
                return {'status': 4}
            gid = GDevRdsInts.execute([get_gid_of_sn(sn)])
            primary = GDevRdsInts.execute([get_dev_primary(sn)])
            if primary:
                return {'status': 5}

            real_ic = GDevRdsInts.execute([get_sn_ic(sn)])
            if real_ic != code:
                return {'status': 6}

            mobile = user_name.split('@')
            mobile = mobile[0] if len(mobile) > 1 else ''
            logger.debug('bind, acc={0}, sn={1}, code={2}'.format(user_name, sn, code))

            GMQDispRdsInts.pipe_execute(
                # sourcer, cb, from, description
                shortcut_mq('cloud_push', push_pack(user_name, 'bind', 2, ':'.join((user_name, sn)), account=sn)),
                shortcut_mq('gen_mysql', mysql_pack(dev_tbl, {'primary': user_name, 'status': 'binded', 'mobile': mobile}, action=2, ref_kvs={'sn': sn}))
            )

            logger.debug('bind push sent')
            GDevRdsInts.pipe_execute(bind_group_primary(gid, sn, user_name), del_ic_sn(code), del_sn_ic(sn))
            return {'status': 2}

        else:
            return {'status': 7}


@route(r'/del_device')
class DelDeviceHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def post(self, user_name, gid):
        primary = GDevRdsInts.execute([get_group_primary(gid)])
        if not primary:
            return {'status': 3}

        followers = GDevRdsInts.execute([get_group_followers(gid)])
        sn = GDevRdsInts.execute([get_sn_of_gid(gid)])

        if primary != user_name and user_name not in followers:
            return {'status': 4}

        # 账号:增加设备和主账号,减少wx账号和操作者账号
        followers.add(primary)
        followers.add(sn)
        followers = filter(lambda u: u[:3] != 'wx#' and u != user_name, followers)

        if primary == user_name:
            for follow in followers:
                GDevRdsInts.pipe_execute(unfollow_group(gid, sn, follow))

                if follow[:3] == 'wx#':
                    GDevRdsInts.execute([hdel_wechat_gid(follow, gid)])
                    logger.debug(u'del wechat follow=%r, gid=%r', follow, gid)
                else:
                    GMQDispRdsInts.execute(
                        [shortcut_mq(
                            'cloud_push',
                            # sourcer, cb, from, description
                            push_pack(user_name, 'del_device', 2, '', account=follow)
                        )]
                    )

            # clean up data
            GDevRdsInts.pipe_execute(unbind_group_primary(gid, sn, primary))

            old_gid = GDevRdsInts.execute([get_old_gid(gid)])
            if old_gid:
                logger.debug('gid={0}, old_gid={1}'.format(gid, old_gid))
                # gid belonged to nice_gid, keep binding with sn
                GMQDispRdsInts.execute([
                    shortcut_mq('gen_mysql', mysql_pack(dev_tbl, {'primary': '', 'status': 'unbound', 'mobile': ''}, action=2, ref_kvs={'sn': sn}))
                ])
            else:
                GMQDispRdsInts.execute([
                    shortcut_mq('gen_mysql', mysql_pack(dev_tbl, {'primary': '', 'status': 'unbound', 'mobile': ''}, action=2, ref_kvs={'sn': sn}))
                ])
            GDevRdsInts.execute([del_all_self_share(sn)])
            all_letters_in = GDevRdsInts.execute([get_letter_inbox(sn, 0, -1)])
            for letter_id in all_letters_in:
                GDevRdsInts.pipe_execute((del_letter_info(letter_id), del_letter_inbox(sn, letter_id)))

            logger.debug('sn={0}'.format(sn))

            return {'status': 1}
        elif user_name in followers:
            GDevRdsInts.pipe_execute(unfollow_group(gid, sn, user_name))

            if user_name[:3] == 'wx#':
                GDevRdsInts.execute([hdel_wechat_gid(user_name, gid)])

            logger.debug('send apns followers:%s'%followers)
            for user in followers:
                GMQDispRdsInts.execute(
                        [shortcut_mq(
                            'cloud_push',
                            # sourcer, cb, from, description
                            push_pack(user_name, 'unfollow', 2, ':'.join((user_name, gid)), account=user)
                        )]
                    )
            return {'status': 2}


@route(r'/invite_follow')
class InviteFollowHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, user_name, guest, gid, msg, file):
        primary = GDevRdsInts.execute([get_group_primary(gid)])
        if primary != user_name:
            return {'status': 1}

        account_exist = GAccRdsInts.execute([exist_account(guest)])
        if not account_exist:
            sql = 'select * from {0} where user_name=%s'.format('ssp_user_login')
            res = self.settings.get('mysql_db').query(sql, guest)
            if len(res) == 0:
                return {'status': 2}
            else:
                # exist in mysql, so we cache it in redis
                pwd = res[0].get('password').encode('utf8')
                GAccRdsInts.execute([set_account_pwd(guest, pwd)])

        sn = GDevRdsInts.execute([get_sn_of_gid(gid)])
        GDevRdsInts.execute([follow_group(gid, sn, guest)])

        payload = ujson.dumps({'master': user_name, 'gid': gid, 'msg': msg, 'file': file, 'action': 'invite_follow'})
        GDevRdsInts.pipe_execute(set_user_group_msglist(guest, gid, 'invite_follow', payload))
        logger.debug('invite follow, guest={0}, gid={1}, payload={2}'.format(guest, gid, payload))

        GMQDispRdsInts.execute(
            [shortcut_mq(
                'cloud_push',
                push_pack(user_name, 'invite_follow', 2, payload, account=guest)

            )]
        )
        return {'status': 0}


@route(r'/reply_follow_invite')
class ReplyFollowInviteHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, user_name, master, gid, reply):
        primary = GDevRdsInts.execute([get_group_primary(gid)])
        if primary != master:
            return {'status': 1}

        if reply == 'Y':
            sn = GDevRdsInts.execute([get_sn_of_gid(gid)])
            GDevRdsInts.pipe_execute(follow_group(gid, sn, user_name))

        GDevRdsInts.execute([del_invite_follow(gid, master, user_name)])
        GMQDispRdsInts.execute(
            [shortcut_mq(
                'cloud_push',
                push_pack(user_name, 'reply_invite_follow', 2, 'reply={0}'.format(reply), account=master)
            )]
        )
        return {'status': 0}


@route(r'/list_followers')
class ListFollowersHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def post(self, user_name, gid):
        primary = GDevRdsInts.execute([get_group_primary(gid)])
        if not primary:
            return {'status': 1}

        nickname = GDevRdsInts.execute([get_user_nickname(primary)])
        ret = {'primary': {primary: nickname}}

        followers = GDevRdsInts.execute([get_group_followers(gid)])

        if followers is None or len(followers) == 0:
            return ret

        followers = list(followers)

        sn = GDevRdsInts.execute([get_sn_of_gid(gid)])
        if not (user_name == primary or user_name == sn or user_name in followers):
            return {'status': 2}

        followers_info = {}
        for user in followers:
            nickname = GDevRdsInts.execute([get_user_nickname(user)])
            followers_info[user] = nickname

        ret['followers'] = followers_info
        return ret


@route(r'/list_devs')
class ListDevsHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def post(self, user_name):
        devs = GDevRdsInts.execute([get_user_devs(user_name)])

        if devs is None or len(devs) == 0:
            return {'status': 1}

        ret = []
        for sn in devs:
            gid = GDevRdsInts.execute([get_gid_of_sn(sn)])
            nickname = GDevRdsInts.execute([get_user_nickname(sn)])
            ret.append({'sn': sn, 'gid': gid, 'nickname': nickname})
        return ret


@route(r'/set_geo_fence')
class SetGeoFenceHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, user_name, sn, lon, lat, radius, name, action):
        primary = GDevRdsInts.execute([get_dev_primary(sn)])
        if user_name != primary:
            return {'status': 1}

        gid = GDevRdsInts.execute([get_gid_of_sn(sn)])
        payload = ujson.dumps({'lon': lon, 'lat': lat, 'rad': radius, 'name': name, 'creator': user_name, 'action': action})

        GDevRdsInts.pipe_execute(set_user_group_msglist(sn, gid, 'geo_fence', payload))

        GMQDispRdsInts.execute(
            [shortcut_mq(
                'cloud_push',
                push_pack(user_name, 'set_geo_fence', 2, payload, account=sn)
            )]
        )

        if action == 'add':
            GDevRdsInts.execute([save_geo_fence(sn, user_name, lon, lat, radius, name)])
        elif action == 'del':
            GDevRdsInts.execute([del_geo_fence(sn, lon, lat, radius)])
        return {'status': 0}


@route(r'/get_geo_fences')
class GetGeoFencesHandler(HttpRpcHandler):
    @web_adaptor()
    @beiqi_tk_sign_wapper()
    def get(self, user_name, pid):
        primary, followers = GDevRdsInts.pipe_execute((get_dev_primary(pid), get_dev_followers(pid)))
        if user_name != primary and user_name not in followers:
            return {'status': 1}

        fences = GDevRdsInts.execute([get_all_geo_fences(pid)])
        return fences