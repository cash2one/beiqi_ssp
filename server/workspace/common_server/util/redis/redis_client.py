#coding:utf-8


from redis import Redis as SyncRedis
from async_redis.redis_client import AsyncRedis
from async_redis.redis_encode import *
from util.convert import resolve_redis_url


class Redis(object):
    def __init__(self, url, sync=True, host='localhost', port=6379, db=0, pwd=None):
        """
        :param url: redis://localhost:6379/0?pwd=xx
        """
        self.__is_sync = sync
        if url:
            #单个db实例
            self.__redis_ob = SyncRedis(*resolve_redis_url(url)) if sync else AsyncRedis(redis_uri=url)
        else:
            if sync:
                self.__redis_ob = SyncRedis(host, port, db, pwd)
            else:
                self.__redis_ob = AsyncRedis(redis_tuple=(host, port, db, pwd))

    def send_cmd(self, *args, **kwargs):
        """
        :param args: redis命令: cmd, key, value, ...
        :param kwargs: 设置事务开关,active_trans=True/False
        """
        if self.__is_sync:
            return getattr(self.__redis_ob, args[0])(*args[1:])
        cmd = 'redis_' + args[0]
        return self.__redis_ob.invoke(globals().get(cmd)(*args[1:]), **kwargs)

    def send_multi_cmd(self, *args):
        """
        :param args: 多条redis命令, 命令间用','分隔
                     每条命令为一个tuple:(cmd, key, value, ...)
        """
        if isinstance(args, (list, tuple)):
            if not args:
                raise ValueError('multi_cmd args at least one')
        if self.__is_sync:
            #pipeline
            p = self.__redis_ob.pipeline()
            p.multi()
            for arg in args:
                getattr(p, arg[0])(*arg[1:])

            resp = p.execute()
            if 1 == len(resp):
                return resp[0]
            return resp
            
        cmds = []
        for arg in args:
            cmd = 'redis_' + arg[0]
            func = globals().get(cmd)
            if func is None:
                raise ValueError('AsyncRedis unsupport cmd:{0}'.format(cmd))
            _ = func(*arg[1:])
            cmds.append(_)

        return self.__redis_ob.invoke(*cmds)