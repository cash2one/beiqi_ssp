#coding:utf-8

from urlparse import urlparse


def build_mongo_url(ip, db_name, port=27017, user="", password=""):
    """构建mongo url
    """

    auth = "" if not user else "{0}:{1}@".format(user, password)
    return "mongodb://{0}{1}:{2}/{3}".format(auth, ip, port, db_name)


def create_mg_con(mongo_url, use_slave=False):
    """创建数据库连接对象

    mongo_url: mongodb://<user>:<pass>@<ip>:<port>/<db>
    """
    from pymongo import Connection

    con = Connection(mongo_url)
    if use_slave:
        con.slave_okay = True
    return con


def create_mg_db(mongo_url, use_slave=False):
    """创建DB对象

    mongo_url: mongodb://<user>:<pass>@<ip>:<port>/<db>
    """

    con = create_mg_con(mongo_url, use_slave)
    return con[urlparse(mongo_url).path[1:]]


def parse_redis_url(url):
    """
    redis://localhost:6379/2
    """
    tmp = urlparse(url)
    ip, port = tmp.netloc.split(':')
    return {'host': ip, 'port': int(port), 'db': tmp.path[1:]}


def create_redis_con(url):
    from redis import Redis

    return Redis(**parse_redis_url(url))
