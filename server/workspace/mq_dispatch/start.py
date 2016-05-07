#coding:utf-8
import msgpack
from redis import Redis as SyncRedis
from random import randint
from tornado.process import fork_processes
from setproctitle import setproctitle
from utils import logger
from util.stream_config_client import conf_load
from util.convert import resolve_redis_url
from collections import defaultdict


mq_conf = dict(conf_load('mq.ini')).get('mq.ini')
setproctitle('mqd_host')


def generate_task_db_ch():
    """
    生成队列任务db与其频道的对应关系
    """
    r = defaultdict(list)

    for s in (s for s in mq_conf.get_sections() if not s.startswith('_')):
        for f in (f for f in mq_conf.get_fields(s) if f.startswith('url_')):
            ip, port, db_list, pwd = resolve_redis_url(mq_conf.get(s, f))
            if isinstance(db_list, int):
                db_list = (db_list, )
            channel = mq_conf.get(s, 'ch')
            for db in db_list:
                r[channel].append(SyncRedis(ip, port, db, pwd))

    return dict(r)

task_ch_redis = generate_task_db_ch()
dispatch_redis = SyncRedis(*resolve_redis_url(mq_conf.get('_dispatch', 'url')))


def watch_dispatch():
    #监听更多通道，分散压力
    watch_channels = [str(x) for x in xrange(1, 11)]
    #兼容
    watch_channels.append('dispatch')
    while 1:
        try:
            _, unpacked_msg = dispatch_redis.blpop(watch_channels, 0)
            unpacked_msg = msgpack.unpackb(unpacked_msg, encoding='utf-8')
            dst_ch = unpacked_msg.get('c')
            redis_list = task_ch_redis.get(dst_ch)
            if not redis_list:
                logger.warn('mis_spell channel: %s' % dst_ch)
                continue
            randin = randint(0, len(redis_list) - 1)
            logger.warn('randin: %s,dst_ch:%s, unpacked_msg:%s' % (randin,dst_ch, unpacked_msg))
            redis_list[randin].rpush(dst_ch, unpacked_msg.get('p'))
        except Exception, ex:
            logger.error('blpop fail: {0}'.format(ex), exc_info=True)


if __name__ == '__main__':
    fork_processes(10)
    setproctitle('mqd_job')
    watch_dispatch()
