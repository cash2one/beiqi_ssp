#coding:utf8
import json
import urllib2
import StringIO
from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers
from tornado.httpclient import HTTPClient
from tornado.httpclient import HTTPRequest
from utils import logger
from util.redis_cmds.circles import get_group_followers
from util.filetoken import gen_file_tk
from util.user import get_user_gids
from setting import *
from util.wechat import gen_wechat_access_token

http_client = HTTPClient()

SELECTED_SOURCES = (0, 16)

file_type_2_msg_type_dic = {
    "1": "image" ,
    "2": "video",
    "3": "voice",
}


def wechat_file_upload(access_token, src_file_url, filename="image.jpg", filetype="image/jpg"):
    """
    微信文件上传
    :param access_token: 访问码
    :param src_file_url: 源url
    :param filename:  文件名： image.jpg
    :param filetype:  文件类型: image/jpg
    :return:  {} 上传结果
    """
    # 在 urllib2 上注册 http 流处理句柄
    register_openers()

    logger.debug('wechat_file_upload: src_file_url=%s', src_file_url)

    # 将beiqi文件上传到微信文件服务器，并获取media_id
    wechat_upload_url = WECHAT_UPLOAD_URL % (access_token, filetype.split("/")[0])
    file_stream = StringIO.StringIO(urllib2.urlopen(src_file_url).read())
    param = MultipartParam(name='media', filename=filename, filetype=filetype, fileobj=file_stream)
    datagen, headers = multipart_encode({"media": param})
    request = urllib2.Request(wechat_upload_url, datagen, headers)
    logger.debug('wechat_file_upload: wechat_upload_url=%s', wechat_upload_url)
    upload_result = json.loads(urllib2.urlopen(request).read())
    logger.debug('wechat_file_upload: wechat_upload_url=%s, upload_result = %r', wechat_upload_url, upload_result)
    return upload_result


def wechat_customer_response(access_token, payload):
    """
    微信客服反馈
    :param access_token: 访问码
    :param payload:  反馈内容
    :return:
    """
    customer_url = WECHAT_CUSTOMER_SERVICE_URL % access_token
    resp = http_client.fetch(HTTPRequest(customer_url, method='POST', body=json.dumps(payload, ensure_ascii=False)))
    logger.debug('send_wechat_file::customer resp customer_url=%s, payload=%s, code = %r, body = %r', customer_url, payload,  resp.code, resp.body)


def wechat_image_sender(wc_openid, file_url):
    """
    微信图片发送器
    :param wc_openid: 微信用户openid
    :param file_url: 远程文件url
    :return:
    """
    assert file_url
    access_token = gen_wechat_access_token(account_cache)

    upload_result = wechat_file_upload(access_token, file_url, "image.jpg", "image/jpg")

    payload = {
        "touser": wc_openid,
        "msgtype": "image",
        "image": {
            "media_id": upload_result.get('media_id')
        }
    }
    wechat_customer_response(access_token, payload)


def wechat_video_sender(wc_openid, file_url):
    """
    微信视频发送器
    :param wc_openid: 微信用户openid
    :param file_url: 远程文件url
    :return:
    """
    assert file_url
    access_token = gen_wechat_access_token(account_cache)

    upload_result = wechat_file_upload(access_token, file_url, "video.amr", "video/amr")

    payload = {
        "touser": wc_openid,
        "msgtype": "video",
        "voice": {
            "media_id": upload_result.get('media_id'),
            "thumb_media_id": "thumb_media_id",
            "title": "title",
            "description":"description"
        }
    }
    wechat_customer_response(access_token, payload)


def wechat_voice_sender(wc_openid, file_url):
    """
    微信语音发送器
    :param wc_openid: 微信用户openid
    :param file_url: 远程文件url
    :return:
    """
    assert file_url
    access_token = gen_wechat_access_token(account_cache)

    upload_result = wechat_file_upload(access_token, file_url, "voice.amr", "voice/amr")

    payload = {
        "touser": wc_openid,
        "msgtype": "voice",
        "voice": {
            "media_id": upload_result.get('media_id')
        }
    }

    wechat_customer_response(access_token, payload)


msg_type_2_wechat_msg_sender = {
    "image": wechat_image_sender,
    "video": wechat_video_sender,
    "voice": wechat_voice_sender,
}


def msg_2_wechat(cli_user, file_type, fn, ref, thumb_fn, thumb_ref, text):
    """
    客户端发送消息给微信用户
    :param cli_user: 客户端用户
    :param file_type:文件类型
    :param fn: 文件名
    :param ref: 文件标识符
    :param thumb_fn: 快照文件名
    :param thumb_ref: 快照文件标识符
    :param text: 文本
    :return: None
    """
    # 查找微信用户
    groups = get_user_gids(cli_user)
    logger.error('msg_2_wechat:cli_user=%s, groups=%r', cli_user, groups)

    followers = set([])
    [followers.update(dev_filter.send_cmd(*get_group_followers(gid))) for gid in groups]

    wechat_followers = filter(lambda user: user[:3] == 'wx#' and user != cli_user, followers)
    logger.error('msg_2_wechat:cli_user=%s, ref=%r, wechat_followers= %r', cli_user, ref, wechat_followers)

    if not wechat_followers:
        return

    msg_type = file_type_2_msg_type_dic.get(file_type, "")
    if not msg_type:
        logger.error('msg_2_wechat not msg_type, file_type=%s', file_type)
        return

    sender = msg_type_2_wechat_msg_sender.get(msg_type)
    if not sender:
        logger.debug('msg_2_wechat not sender：msg_type=%s', msg_type)
        return

    logger.debug('msg_2_wechat sender：sender=%s', sender.__name__)

    tk = gen_file_tk(cli_user, fn, 0, 0)
    file_url = SSP_DOWNLOAD_FILE_URL % (tk, ref)
    [sender(wc_user.split("#")[1], file_url) for wc_user in wechat_followers]

