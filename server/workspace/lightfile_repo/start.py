#coding:utf-8
from setproctitle import setproctitle
from tornado.ioloop import IOLoop
from utils import logger
from util.in_server import IncomingServer
from util.convert import parse_ip_port
from util.stream_config_client import conf_load
from level_core import resolve


def handle_req(req):
    req.write(resolve(*req.args))
    req.finish()


def main():
    logger.init_log('lvl_core', 'lvl_core')
    setproctitle('lvl:core')
    IncomingServer(handle_req, log=False).listen(
        parse_ip_port(dict(conf_load('leveldb.ini')).get('leveldb.ini').get('default', 'host'))[-1]
    )
    IOLoop.instance().start()


if __name__ == "__main__":
    main()