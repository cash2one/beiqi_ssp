#coding: utf8
import site, os; site.addsitedir(os.path.dirname(os.path.realpath(__file__))); site.addsitedir(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))); site.addsitedir(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "common_server"))
import ujson
import time
from utils import logger
from utils.network.http import HttpRpcClient
from util.redis_cmds.wechat import set_wechat_access_token,set_wechat_ticket
from config import GAccRdsInts
from setting import WX_GET_ACCESS_TOKEN_URL, WX_GET_TICKER_URL
from setproctitle import setproctitle


logger.init_log("get_access_token", "get_access_token")
setproctitle("s_get_access_token")


def get_access_token():
    get_token_result = ujson.loads(HttpRpcClient().fetch_async(url=WX_GET_ACCESS_TOKEN_URL))
    access_token = get_token_result.get('access_token')
    assert access_token, 'get wechat access token failed. errcode: %r, errmsg: %r' % (get_token_result.get('errcode'), get_token_result.get('errmsg'))
    expires = get_token_result.get('expires_in')
    GAccRdsInts.send_cmd(*set_wechat_access_token(access_token, expires))
    logger.debug('get_access_token:%s, access_token=%s, expires_in=%s', time.strftime('%Y-%d-%m %H:%M:%S', time.localtime()), access_token, expires)
    return access_token, expires


def get_ticker(access_token):
    get_ticket_result = ujson.loads(HttpRpcClient().fetch_async(url=WX_GET_TICKER_URL.format(access_token=access_token)))
    ticker = get_ticket_result.get("ticker")
    ticker_exp = get_ticket_result.get('expires_in')
    GAccRdsInts.send_cmd(*set_wechat_ticket(ticker, ticker_exp))
    logger.debug('get_ticker:%s, ticker=%s, expires_in=%s', time.strftime('%Y-%d-%m %H:%M:%S', time.localtime()), ticker, ticker_exp)
    return ticker


while True:
    access_token, expires = get_access_token()
    get_ticker(access_token)
    time.sleep(int(expires) - 10)
