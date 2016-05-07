#coding: utf8
import urllib
from utils import logger
from util.mq_packs.uni_pack import shortcut_mq
from util.mq_packs.cloud_push_pack import pack as push_pack
from util.convert import bs2utf8
from config import GMQDispRdsInts


def wechat_2_device(author, file_type, fn, ref, thumb_fn="", thumb_ref="", text=""):
    logger.debug('wechat_2_device author={0}, type={1}, fn={2}, ref={3}, thumb_fn={4}, thumb_ref={5}, text={6}'.format(author, file_type, fn, ref, thumb_fn, thumb_ref, text))

    des = bs2utf8(':'.join([urllib.quote(bs2utf8(v)) for v in (author,  file_type, fn, ref, thumb_fn, thumb_ref, text)]))

    GMQDispRdsInts.send_cmd(
        *shortcut_mq(
            'wechat_msg',
            push_pack(author, 'msg', 2, des)
        )
    )