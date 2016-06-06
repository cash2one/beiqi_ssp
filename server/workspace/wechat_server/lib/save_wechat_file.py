#coding: utf8
import ujson
import urllib
from utils import logger
from utils.network.http import HttpRpcClient
from util.filetoken import gen_file_tk
from util.redis_cmds.wechat import get_wechat_access_token
from util.convert import bs2utf8
from config import GAccRdsInts
from setting import BEIQI_FILE_UP_URL, WX_MEDIA_DOWN_URL


def save_wechat_file(pic_url, from_user_name, msg_id, file_type, create_time, media_id=''):
    if file_type == '1':
        url = pic_url
        fn = msg_id + '.jpg'
    elif file_type == '2' or file_type == '3':
        token = GAccRdsInts.send_cmd(*get_wechat_access_token())

        url = WX_MEDIA_DOWN_URL.format(token, media_id)

    logger.debug('url = %s'%url)
    img = None
    try:
        for _ in xrange(3):
            img = HttpRpcClient().fetch_async(url=url)
            if img.code == 200:
                break
    except Exception, ex:
        logger.debug(u'url = %r, img = %r', url, img)
        logger.error(u'get wechat file failed: {0}'.format(ex), exc_info=True)

    if media_id:
        fn = bs2utf8(img.headers.get('Content-disposition').split(';')[1].split('=')[1].strip('"'))
        logger.debug('fn = %r', fn)
        content_type = img.headers.get('Content-Type')
        logger.debug(u'content_type = %s' % content_type)
        if content_type.split('/')[0] == 'image':
            file_type = '1'

    logger.debug(u'from_user_name=%s, fn=%s', from_user_name, fn)
    ul = 0
    by_app = 0
    tk = gen_file_tk(from_user_name, fn, ul, by_app)
    logger.debug(u'save wechat file. tk = %r' % tk)
    up_args = {'tk': tk, 'src': file_type, 'by': from_user_name, 'usage': 'share'}
    for _ in xrange(3):
        logger.debug(u'save wechat file. up_url = %s' % (BEIQI_FILE_UP_URL + urllib.urlencode(up_args)))
        resp = HttpRpcClient().fetch_async(url=BEIQI_FILE_UP_URL + urllib.urlencode(up_args), body=img.body)
        if resp.code == 200:
            break
    if resp.code != 200:
        logger.error(u'file up resp.code = %r', resp.code)
        return None
    logger.debug(u'file up resp.code = %r', resp.code)
    resp = ujson.loads(resp.body)
    return fn, tk, resp.get('r')