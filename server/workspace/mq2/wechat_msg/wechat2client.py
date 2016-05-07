#coding:utf8
import ujson
import urllib2
import StringIO
from utils import logger
from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers
from utils.network.http import HttpRpcClient
from util.redis_cmds.circles import get_wechat_gids, get_user_groups, get_group_followers, get_gid_of_sn
from util.redis_cmds.wechat import get_wechat_access_token
from util.filetoken import gen_file_tk
from setting import *
from config import GDevRdsInts, GAccRdsInts


SELECTED_SOURCES = (0, 16)

file_type_2_msg_type_dic = {
    "1": "image" ,
    "2": "video",
    "3": "voice",
}

def wechat_2_client_msg(mqtt_client, wc_user, msg):
    """
    微信用户消息广播到客户端
    :param mqtt_client:mqtt客户端
    :param wc_user: 微信用户
    :param msg: 需要发送的消息
    :return:
    """
    gid_list = GDevRdsInts.send_cmd(*get_wechat_gids(wc_user))
    logger.debug('wechat_2_client: gid_list=%r, author=%r, payload:%r', gid_list, wc_user, msg)
    [mqtt_client.publish(PUB_BEIQI_MSG_BCAST.format(gid), msg) for gid in gid_list]


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
    upload_result = ujson.loads(urllib2.urlopen(request).read())
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
    resp = HttpRpcClient().fetch_async(url=customer_url, body=ujson.dumps(payload, ensure_ascii=False))
    logger.debug('send_wechat_file::customer resp customer_url=%s, payload=%s, code = %r, body = %r', customer_url, payload,  resp.code, resp.body)

def wechat_image_sender(wc_openid, file_url):
    """
    微信图片发送器
    :param wc_openid: 微信用户openid
    :param file_url: 远程文件url
    :return:
    """
    assert file_url
    access_token = GAccRdsInts.send_cmd(*get_wechat_access_token())

    upload_result = wechat_file_upload(access_token, file_url, "image.jpg", "image/jpg")

    payload = {
        "touser": wc_openid,
        "msgtype": "image",
        "voice": {
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
    access_token = GAccRdsInts.send_cmd(*get_wechat_access_token())

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
    access_token = GAccRdsInts.send_cmd(*get_wechat_access_token())

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


def is_device(acc):
    return "@" not in acc and "wx#" not in acc

def client_2_wechat_msg(cli_user, file_type, fn, ref, thumb_fn, thumb_ref, text):
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
    groups = [GDevRdsInts.send_cmd(*get_gid_of_sn(cli_user))] \
        if is_device(cli_user) \
        else GDevRdsInts.send_cmd(*get_user_groups(cli_user))

    logger.debug('client_2_wechat_msg:cli_user=%s, groups=%r', cli_user, groups)

    followers = set([])
    [followers.update(GDevRdsInts.send_cmd(*get_group_followers(gid))) for gid in groups]

    wechat_followers = filter(lambda user: user[:3] == 'wx#' and user != cli_user, followers)
    logger.debug('client_2_wechat_msg:cli_user=%s, ref=%r, wechat_followers= %r', cli_user, ref, wechat_followers)

    if not wechat_followers:
        return

    msg_type = file_type_2_msg_type_dic.get(file_type, "")
    if not msg_type:
        logger.debug('client_2_wechat_msg not msg_type, file_type=%s', file_type)
        return

    sender = msg_type_2_wechat_msg_sender.get(msg_type)
    if not sender:
        logger.debug('client_2_wechat_msg not sender：msg_type=%s', msg_type)
        return

    logger.debug('client_2_wechat_msg sender：sender=%r', sender)

    tk = gen_file_tk(cli_user, fn, 0, 0)
    file_url = SSP_DOWNLOAD_FILE_URL % (tk, ref)
    [sender(wc_user.split("#")[1], file_url) for wc_user in wechat_followers]