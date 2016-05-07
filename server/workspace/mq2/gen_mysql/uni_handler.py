#coding:utf-8
import torndb
from util.stream_config_client import load as conf_load
from utils import logger
from util.sql_expr import exec_sql
from util.redis.redis_client import Redis
from util.mq_packs.uni_pack import shortcut_mq


group = dict(conf_load('mysql.ini', 'mq.ini'))
mysql_db = torndb.Connection(**group.get('mysql.ini').get_fields('cms'))
mq_conf = group.get('mq.ini')
uni_mq = Redis(mq_conf.get('_dispatch', 'url'))


def _re_notify(pk, packet):
    """
    重新投递
    :param pk: 主键
    :param packet:
    """
    #非mysql频道的投递
    _non_ms = packet.get('_non_mysql')
    if isinstance(_non_ms, dict):
        yield shortcut_mq(_non_ms.get('mqc'), _non_ms.get('mqp'))

    #一次性提交多个外键任务
    for k, is_ms in packet.iteritems():
        if not k.startswith('_mysql'):
            continue
        if not is_ms:
            continue

        table_name, fk, ob = is_ms
        if not ob:
            continue
        if isinstance(ob, dict):
            ob.update({fk: pk})
        elif isinstance(ob, (list, tuple)):
            [x.update({fk: pk}) for x in ob]
        try:
            #异常后不至于影响其他调用
            exec_sql(mysql_db, table_name, ob, 0)
        except Exception, ex:
            logger.error('mysql fail: {0}'.format(ex), exc_info=True)


def handle_msg(packet):
    """
    prj字段已废弃
    """
    tn = packet.get('tn')
    logger.debug('packet=%r' % packet)

    try:
        pk = exec_sql(mysql_db, tn, packet.get('pld'), packet.get('act'), packet.get('key'), *packet.get('tsf'))
        ren = tuple(_re_notify(pk, packet))
        if not ren:
            return
        uni_mq.send_multi_cmd(*ren)
    except Exception, ex:
        logger.error('exec sql fail: {0}, {1}'.format(packet, ex), exc_info=True)
