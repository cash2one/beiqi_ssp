#coding:utf-8


import re
from util.convert import parse_ip_port


pattern = re.compile(r'^592F(?P<index>\d+)$')


def resolve_port(conf, mode):
    """
    监听端口按照基端口累加
    :param conf: 配置对象
    :param mode: 运行模式
    :return:
    """
    base_port = parse_ip_port(conf.get('_default', 'host'))[-1]
    m = pattern.search(mode)
    if not m:
        return base_port
    return base_port + int(m.groupdict().get('index'))