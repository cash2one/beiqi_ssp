#coding:utf8
import urllib
import ujson
from tornado.httpclient import HTTPClient
from tornado.httpclient import HTTPRequest
from util.redis_cmds.wechat import get_wechat_access_token
from utils import logger
from util.configx import conf_file
from util.redis.redis_client import Redis

redis_conf = conf_file('../configs/redis.ini')
_account_cache = Redis(redis_conf.get('oauth', 'url'))


http_client = HTTPClient()

token = _account_cache.send_cmd(*get_wechat_access_token())
url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token={0}'.format(token)

menu = {
     "button":[
	{
           "name": "智慧互联",
           "sub_button":[
           {
          	"type":"view",
          	"name":"绑定平板",
          	"url": "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxd0334fe5bbc270d2&redirect_uri=http://wechatapi.beiqicloud.com:8108/wechat/pages/add_device&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect",
       	    },
	    {
		"type":"view",
	        "name":"管理平板",
		"url":"https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxd0334fe5bbc270d2&redirect_uri=http://wechatapi.beiqicloud.com:8108/wechat/pages/manage_dev?response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect",
	    },
		   {
		"type":"view",
	        "name":"配置AirKiss",
		"url":"http://wechatapi.beiqicloud.com/wechat/pages/search_device",
	    }]
	},
	{
            "type": "view",
            "name": "使用帮助",
       	    "url": "http://wechatapi.beiqicloud.com:8108/wechat/pages/user_guide"
	},
	{
            "name": "关于我们",
            "sub_button": [
	    {
		"type":"view",
		"name":"购买平板",
		"url":"http://120.25.94.227/buy/",
	    },
	    {
		"type":"view",
		"name":"下载APP",
		"url":"http://120.25.94.227/app/"
	    },
	    {
		"type":"view",
		"name":"公司简介",
		"url":"http://120.25.94.227/propagate/company/"
	    }]
	}]
 }


jbody = ujson.dumps(menu, ensure_ascii=False)

resp =  http_client.fetch(HTTPRequest(url, method='POST', headers={'content-type': 'application/json'}, body=jbody))
print resp.body
j = ujson.loads(resp.body)
errcode = j.get('errcode')
errmsg = j.get('errmsg')
if int(errcode) != 0:
    logger.error('create wechat menu failed. errcode: %r, errmsg: %r', errcode, errmsg)
else:
    logger.debug('create menu.errcode=%s, errmsg=%s', errcode, errmsg)
