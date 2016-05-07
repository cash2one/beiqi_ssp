#coding: utf8
import ujson
from tornado.httpclient import HTTPClient
from tornado.httpclient import HTTPRequest
from utils import logger
from util.redis_cmds.wechat import set_wechat_access_token,set_wechat_ticket
import time
from util.configx import conf_file
from util.redis.redis_client import Redis

redis_conf = conf_file('../configs/redis.ini')

_account_cache = Redis(redis_conf.get('oauth', 'url'))

http_client = HTTPClient()

APPID = 'wxd0334fe5bbc270d2'
APPSECRET = '6d2f605d568f6a66f2acd6736befa8e3'
url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}'.format(APPID, APPSECRET)

WEIXIN_GET_TICKER_URL = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?type=jsapi&access_token=%s'

while True:
    resp =  http_client.fetch(HTTPRequest(url, method='POST', body=''))
    print resp.body
    j = ujson.loads(resp.body)
    if 'access_token' not in j:
        logger.error('get wechat access token failed. errcode: %r, errmsg: %r', j.get('errcode'), j.get('errmsg'))
    else:
        token = j.get('access_token')
        expires = j.get('expires_in')
        _account_cache.send_cmd(*set_wechat_access_token(token,expires))

        get_ticket_result = http_client.fetch(HTTPRequest(WEIXIN_GET_TICKER_URL%token, method='GET'))
        ticket = get_ticket_result.get("ticker")
        ticker_exp = j.get('expires_in')
        _account_cache.send_cmd(*set_wechat_ticket(ticket, ticker_exp))

        logger.debug('%s, access_token=%s, expires_in=%s', time.strftime('%Y-%d-%m %H:%M:%S', time.localtime()), token, expires)
        time.sleep(int(expires) - 10)
