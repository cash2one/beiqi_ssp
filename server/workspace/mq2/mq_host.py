#coding:utf-8
import sys
from utils import logger
from util.convert import resolve_redis_url
from tornado.process import fork_processes
import msgpack
from tornado.ioloop import IOLoop
from tornado.concurrent import TracebackFuture, Future
from tornado.options import options
from setproctitle import setproctitle
from util.stream_config_client import load as conf_load
from util.load import import_object
from util.redis.redis_client import Redis as AsyncRedis
from tornado.gen import coroutine
from util.convert import parse_ip_port
from util.internal_forward.gen_internal_client import GeneralInternalClient

redis_conf = dict(conf_load('redis.ini')).get('redis.ini')
leveldb_conf = dict(conf_load('leveldb.ini')).get('leveldb.ini')

@coroutine
def consume_mq():
    """
    执行单个任务
    :return:
    """
    resp = yield watch_redis.send_cmd('blpop', 0, watch_channel, active_trans=False)
    if resp is None:
        return
    _, raw_msg = resp
    unpacked_msg = msgpack.unpackb(raw_msg, encoding='utf-8')
    del raw_msg

    h = handler_map.get(watch_channel)
    if not h:
        logger.warn('no handler for {0}'.format(watch_channel))
        return
    logger.warn('consume_mq {0} {1}'.format(h,unpacked_msg))
    h(unpacked_msg)


def coroutine_run():
    """
    执行协程
    """
    try:
        result = consume_mq()
    except Exception:
        future = TracebackFuture()
        future.set_exc_info(sys.exc_info())
    else:
        assert isinstance(result, Future)
        future = result

    def consumer_finish(f):
        """
        重新启动ioloop回调
        :param f:
        """
        if f.exc_info() is not None:
            logger.warn(f.exc_info())
        elif f.exception() is not None:
            logger.warn(f.exception())

        IOLoop.current().add_callback(coroutine_run)

    IOLoop.current().add_future(future, consumer_finish)


def run_process(redis_url, process_ratio, run_or_not):
    """
    通过load_conf.py读取配置，统一加载

    :param redis_url: 监控redis地址
    :param process_ratio: 启动进程数
    :param run_or_not: 是否启动该进程
    :return:
    """
    host, port, db, pwd, channel = resolve_redis_url(redis_url, True)
    logger.init_log(channel, channel)

    if not (redis_url and isinstance(redis_url, str) and '|' not in redis_url):
        logger.fatal('redis_url invalid: %s' % redis_url)
        return
    if not isinstance(process_ratio, int):
        logger.fatal('process_ratio invalid: %s' % type(process_ratio))
        return
    if not isinstance(run_or_not, int):
        logger.fatal('run param invalid: %s' % type(run_or_not))
        return

    if not run_or_not:
        logger.debug('not run {0} via config'.format(redis_url))
        return
    setproctitle('mq:host:{0}'.format(channel))

    fork_processes(process_ratio)
    options.logging = 'error'
    setproctitle('mq:{0}:{1}'.format(channel, db))

    loop = IOLoop.instance()

    setattr(__builtins__, 'handler_map', {})
    setattr(__builtins__, 'watch_redis', AsyncRedis(None, False, host, port, db, pwd))
    setattr(__builtins__, 'watch_channel', channel)
    setattr(__builtins__, 'dev_filter', AsyncRedis(redis_conf.get('dev_filter', 'url')))
    setattr(__builtins__, 'level_client', GeneralInternalClient(parse_ip_port(leveldb_conf.get('default', 'host'))))
    setattr(__builtins__, 'account_cache', AsyncRedis(redis_conf.get('oauth', 'url')))

    logger.warn('run_process channel:{0}, db:{1}, redis_url={2}'.format(channel, db, redis_url))

    # 导入handler模块
    mod_name = '.'.join((channel, 'uni_handler', 'handle_msg'))
    handler = import_object(mod_name)
    logger.warn('import mod:{0}'.format(mod_name))
    if handler:
        logger.warn('found handler={0}'.format(mod_name))
        handler_map.update({channel: handler})

    loop.add_callback(coroutine_run)
    loop.start()


def main():
    """
    启动参数加入进程数，单个进程是否启动
    """
    if 2 != len(sys.argv):
        return
    redis_url, process_ratio, run_or_not = sys.argv[1].split('|')
    process_ratio = int(process_ratio)
    run_or_not = int(run_or_not)
    run_process(redis_url, process_ratio, run_or_not)


if __name__ == '__main__':
    main()
