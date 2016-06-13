#coding: utf-8
from tornado import httpserver
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.web import RequestHandler
from util.redis.redis_client import Redis as AsyncRedis
from util.stream_config_client import conf_load
from util.wechat import gen_wechat_access_token

redis_conf = dict(conf_load('redis.ini')).get('redis.ini')
account_cache = AsyncRedis(redis_conf.get('oauth', 'url'))


class GetAccessTokenHandler(RequestHandler):
    def get(self):
        self.finish(gen_wechat_access_token(account_cache))


def main():
    app = Application(
        (
            ('/access_token', GetAccessTokenHandler),
        ))

    server = httpserver.HTTPServer(app)
    server.bind(20000)
    server.start(1)

    IOLoop.instance().start()


if __name__ == '__main__':
    main()

