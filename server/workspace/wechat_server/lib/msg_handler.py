#coding: utf8
import json
import re
import time
from utils import logger
from util.convert import bs2utf8
from lib.add_device import add_device, wechat_reply_template
from lib.wechat_2_device import wechat_2_device
from lib.wechat_share import wechat_share
from save_wechat_file import save_wechat_file

txt_return_template = '<xml>\
<ToUserName><![CDATA[{0}]]></ToUserName>\
<FromUserName><![CDATA[{1}]]></FromUserName>\
<CreateTime>{2}</CreateTime>\
<MsgType><![CDATA[{3}]]></MsgType>\
<Content><![CDATA[{4}]]></Content>\
</xml>'

gid_pattern = re.compile(r'^[^0]{1}[0-9]{5}$')

fromUserName = 'gh_a9e7d5d5933e'

msg_type_2_file_type_dic = {
    "image": "1",
    "shortvideo": "2",
    "voice": "3"
}


def get_wechat_user(ele_tree):
    return 'wx#' + ele_tree.find('FromUserName').text


def mk_share_file(fn, ref, thumb_fn, thumb_ref):
    file_dic = {fn: ref} if not thumb_fn else {fn: ref, thumb_fn: thumb_ref}
    file_u8 = dict([(bs2utf8(k), bs2utf8(v)) for k, v in file_dic.items()])
    return json.dumps(file_u8)


def wechat_handler_warp(func):
    def wrapper(req_handler, ele_tree, *args, **kwargs):
        msg_type = ele_tree.find('MsgType').text
        create_time = ele_tree.find('CreateTime').text
        username = get_wechat_user(ele_tree)
        msg_id = ele_tree.find('MsgId').text

        file_type = msg_type_2_file_type_dic[msg_type]

        wechat_ret = func(req_handler, ele_tree, file_type, create_time, username, msg_id, *args, **kwargs)
        logger.debug(u'wechat_ret=%s', wechat_ret)

        reply = 'success'
        err_msg = wechat_ret.get('err_msg', '')
        if err_msg:
            reply = txt_return_template.format(username[3:], fromUserName, str(int(time.time())), 'text', err_msg)
        else:
            fn = wechat_ret['fn']
            ref = wechat_ret['ref']
            thumb_fn = wechat_ret.get('thumb_fn', '')
            thumb_ref = wechat_ret.get('thumb_ref', '')

            resp = wechat_share(username, file_type, mk_share_file(fn, ref, thumb_fn, thumb_ref))
            logger.debug(u'%s. resp = %s', func.__name__, resp)

            wechat_2_device(username, file_type, fn, ref, thumb_fn, thumb_ref)

        req_handler.finish(reply)
    return wrapper


@wechat_handler_warp
def text_handler(req_handler, ele_tree, file_type, create_time, username, msg_id):
    content = ele_tree.find('Content').text
    if content[0] == '#' and gid_pattern.match(content[1:]):
        gid = content[1:]
        status = json.loads(add_device(username, gid))
        return {'err_msg': wechat_reply_template.get(status.get('status'))}


@wechat_handler_warp
def image_handler(req_handler, ele_tree, file_type, create_time, username, msg_id):
    pic_url = ele_tree.find('PicUrl').text
    _ = save_wechat_file(pic_url, username, msg_id, file_type, create_time)
    if _ is None:
        logger.debug('save file failed.')
        return {'err_msg': '保存文件失败,请重试.'}

    fn, tk, ref = _
    return {"fn": fn, "ref": ref}


@wechat_handler_warp
def video_handler(req_handler, ele_tree, file_type, create_time, username, msg_id):
    pic_url = ''
    media_id = ele_tree.find('MediaId').text
    _ = save_wechat_file(pic_url, username, msg_id, file_type, create_time, media_id)
    if _ is None:
        logger.debug('save file failed.')
        return {'err_msg': '保存文件失败,请重试.'}

    fn, tk, ref = _

    thumbMediaId = ele_tree.find('ThumbMediaId').text
    _ = save_wechat_file(pic_url, username, msg_id, file_type, create_time, thumbMediaId)
    if _ is None:
        logger.debug('save file failed.')
        return {'err_msg': '保存文件失败,请重试.'}

    thumb_fn, thumb_tk, thumb_ref = _
    return {"fn": fn, "ref": ref, "thumb_fn": thumb_fn, "thumb_ref": thumb_ref}


@wechat_handler_warp
def voice_handler(req_handler, ele_tree, file_type, create_time, username, msg_id):
    pic_url = ''
    media_id = ele_tree.find('MediaId').text
    _ = save_wechat_file(pic_url, username, msg_id, file_type, create_time, media_id)
    if _ is None:
        logger.debug('save file failed.')
        return {'err_msg': '保存文件失败,请重试.'}

    fn, tk, ref = _
    return {"fn": fn, "ref": ref}


msg_handlers = {
    "text": text_handler,
    "image": image_handler,
    "shortvideo": video_handler,
    "voice": voice_handler
}