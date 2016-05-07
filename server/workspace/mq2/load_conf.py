#coding:utf-8
import site, os; site.addsitedir(os.path.dirname(os.path.realpath(__file__))); site.addsitedir(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))); site.addsitedir(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "common_server"))
from utils import logger
from util.stream_config_client import load as conf_load
from util.convert import resolve_redis_url


mq_conf = dict(conf_load('mq.ini')).get('mq.ini')
#单通道默认进程数，通过 ratio 字段覆盖
default_process_ratio = mq_conf.get('_task', 'process_ratio')
#单通道是否启动，通过 run 字段覆盖
run_process = mq_conf.get('_task', 'run_process')


for section in (s for s in mq_conf.get_sections() if not s.startswith('_')):
    ratio = mq_conf.get(section, 'ratio') or default_process_ratio
    run_or_not = mq_conf.get(section, 'run') or run_process

    for field in (f for f in mq_conf.get_fields(section) if f.startswith('url_')):
        host, port, db_list, pwd = resolve_redis_url(mq_conf.get(section, field))
        channel = mq_conf.get(section, 'ch')
        if isinstance(db_list, int):
            db_list = (db_list, )
        for db in db_list:
            #通过|分隔参数
            output = '|'.join((
                'redis://{0}:{1}/{2}?pwd={3}#{4}'.format(host, port, db, pwd, channel),
                ratio,
                run_or_not
            ))
            logger.debug('>> {0}'.format(output))
            print output