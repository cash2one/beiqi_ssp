#coding:utf-8
import site, os; site.addsitedir(os.path.dirname(os.path.realpath(__file__))); site.addsitedir(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))); site.addsitedir(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "common_server"))
from utils import logger
from tornado.ioloop import IOLoop
from setproctitle import setproctitle
from util.in_server import IncomingServer
from util.convert import parse_ip_port
from util.stream_config_client import load as conf_load
from util.convert import redis_encode_batch
from apns_con_pool import queue_push


apns_conf = dict(conf_load('apns.ini')).get('apns.ini')


def handle_req(req):
    queue_push(apns_conf, *req.args)
    req.write(redis_encode_batch(1))
    req.finish()


def main():
    logger.init_log('apns_agent', 'apns_agent')
    setproctitle('apns:agent')
    svr = IncomingServer(handle_req, log=False)
    svr.bind(parse_ip_port(apns_conf.get('_default', 'host'))[-1])
    svr.start(0)
    IOLoop.instance().start()


if __name__ == '__main__':
    main()