# coding=utf-8
"""
Created on 2015-05-15

@author: jay
"""
import platform
import datetime
from utils.meta.instance_pool import InstancePool
from utils.data.coordinator import CacheCoordinator


if platform.system() == 'Linux':
    from credis import Connection
    from credis.geventpool import ResourcePool
    MAX_POOL_SIZE = 32
else:
    import redis

# 支持的命令
cmd_support = {'get':     ['get', 'GET'],
               'set':     ['set', 'SET'],
               'expire':  ['expire', 'EXPIRE'],
               'delete':  ['delete', 'DELETE', 'del', 'DEL'],
               'keys':    ['keys', 'KEYS']}


DB_SIZE = 16

def choice_db(factor):
    return factor % DB_SIZE

def assert_redis_true(cmds, results):
    assert isinstance(cmds, list) or isinstance(results, tuple)
    assert isinstance(results, list) or isinstance(results, tuple)
    for idx, _ in enumerate(cmds):
            assert results[idx]


# set redis 命令合成处理
def make_redis_set_cmd(*args):
    """
    @param set_cmd:完整set命令 ['set',k,v,x,x,x,x]
    @return redis set format
    """
    # set k v
    pieces = [args[0], args[1], args[2]] 
    if len(args) > 3:
        ex = args[3]
        pieces.append('EX')
        if isinstance(ex, datetime.timedelta):
            ex = ex.seconds + ex.days * 24 * 3600
        pieces.append(ex)
    if len(args) > 4:
        px = args[4]
        pieces.append('PX')
        if isinstance(px, datetime.timedelta):
            ms = int(px.microseconds / 1000)
            px = (px.seconds + px.days * 24 * 3600) * 1000 + ms
        pieces.append(px)
    if len(args) > 5:
        pieces.append('NX')
    if len(args) > 6:
        pieces.append('XX')
    return pieces
    

class RedisClient(object):
    """
    Redis 客户端管理器
    """
    __metaclass__ = InstancePool

    def __init__(self, ip, port, db=0, pwd=None):
        self.sip = ip
        self.sport = port
        self.sdb = db
        self.spwd = pwd if pwd else None
        
        if platform.system() == 'Linux':
            self.redis_pool = ResourcePool(MAX_POOL_SIZE,
                                           Connection,
                                           host=self.sip,
                                           port=self.sport,
                                           db=self.sdb,
                                           password=self.spwd)
        else:
            self.redis_pool = redis.ConnectionPool(host=self.sip,
                                                   port=self.sport,
                                                   db=self.sdb,
                                                   password=self.spwd)
        self.ping()
    
    def ping(self):
        conn = self.get_conn()
        err_msg = 'redis server[%s:%s] not exist!!' % (self.sip, self.sport)
        if platform.system() == 'Linux':
            assert conn.execute('PING'), err_msg
        else:
            assert conn.ping(), err_msg
    
    def get_conn(self):
        if platform.system() == 'Linux':
            conn = self.redis_pool
        else:
            conn = redis.Redis(connection_pool=self.redis_pool)
        return conn
    
    def set(self, *args, **kwargs):
        """
        args = k,v,ex,nx,px,xx
        """
        pipe = kwargs.get('pipe')
        conn = self.get_conn()if pipe is None else pipe
            
        if platform.system() == 'Linux':
            set_cmd = make_redis_set_cmd('SET', *args)
            res = conn.execute(*set_cmd)
        else:
            res = conn.set(*args)
        return res
    
    def get(self, *args, **kwargs):
        """
        args = k
        """
        pipe = kwargs.get('pipe')
        conn = self.get_conn()if pipe is None else pipe
                    
        if platform.system() == 'Linux':
            res = conn.execute('GET', *args)
        else:
            res = conn.get(*args)
        return res
    
    def expire(self, *args, **kwargs):
        """
        args = k,et
        """
        pipe = kwargs.get('pipe')
        conn = self.get_conn()if pipe is None else pipe
        
        if platform.system() == 'Linux':
            res = conn.execute('EXPIRE', *args)
        else:
            res = conn.expire(*args)
        return res
    
    def delete(self, *args, **kwargs):
        """
        args = *names
        """
        pipe = kwargs.get('pipe')
        conn = self.get_conn()if pipe is None else pipe
        
        if platform.system() == 'Linux':
            res = conn.execute('DEL', *args)
        else:
            res = conn.delete(*args)
        return res
    
    def keys(self, *args, **kwargs):
        """
        args = *pattern
        """
        pipe = kwargs.get('pipe')
        conn = self.get_conn()if pipe is None else pipe
        
        if platform.system() == 'Linux':
            res = conn.execute('KEYS', *args)
        else:
            res = conn.keys(*args)
        return res
    
    def execute(self, cmd, pipe=None):
        """
        执行redis命令
        cmd = (oper,k,v,,,,)
        """
        if cmd[0] in cmd_support['get']:
            res = self.get(*cmd[1:], pipe=pipe)
        elif cmd[0] in cmd_support['set']:
            res = self.set(*cmd[1:], pipe=pipe)
        elif cmd[0] in cmd_support['expire']:
            res = self.expire(*cmd[1:], pipe=pipe)
        elif cmd[0] in cmd_support['delete']:
            res = self.delete(*cmd[1:], pipe=pipe)
        elif cmd[0] in cmd_support['keys']:
            res = self.keys(*cmd[1:], pipe=pipe)
        return res
    
    def pipe_execute(self, cmds):
        """
        执行redis管道命令
        cmds = [(oper,k,v),,,]
        """
        if platform.system() == 'Linux':
            for idx, cmd in enumerate(cmds):
                if cmd[0] in cmd_support['set']:
                    cmds[idx] = make_redis_set_cmd(*cmd)
            res = self.redis_pool.execute_pipeline(*cmds)
        else:
            conn = self.get_conn()
            pipe = conn.pipeline()
            for cmd in cmds:
                self.execute(cmd, pipe)
            res = pipe.execute()
        return res


class RedisCoordinator(CacheCoordinator):
    """
    redis数据操作协调器
    """
    def __init__(self, cache_operator, storage_operator, cache_picker, ceche_timeout=3600 * 8):
        super(RedisCoordinator, self).__init__(cache_operator, storage_operator, cache_picker, ceche_timeout)
        self.redis_client = cache_operator
        self.storage_operator = storage_operator
        self.cache_picker = cache_picker
        self.ceche_timeout = ceche_timeout

    def set(self, key, value):
        """
        同时设置redis和storage
        :param key:
        :param value:
        :return:
        """
        self.storage_operator.set(key, value)
        assert self.redis_client.set(self.cache_picker.pick_key(key),
                                     self.cache_picker.pick_value(value),
                                     self.ceche_timeout)

    def get_ls(self, keys):
        """
        同步加载storage和缓存的数据，如果缓存不存在，从db加载，并同时同步缓存
        :param keys:
        :return: [value,,,]
        """
        if not keys:
            return []

        # get cache
        cmds = [['get', self.cache_picker.pick_key(k)] for k in keys]
        cache_ls = self.redis_client.pipe_execute(cmds)
        cache_ls = [self.cache_picker.unpick_value(data) if data else None for data in cache_ls]

        # load storage for miss cache
        miss_cache_keys = [k for i, k in enumerate(keys) if cache_ls[i] is None]
        miss_cache_ls = self.storage_operator.get_ls(miss_cache_keys) if miss_cache_keys else []

        # add miss cache
        add_cache_cmds = []
        miss_cache_dic = {}
        for idx, key in enumerate(miss_cache_keys):
            value = miss_cache_ls[idx]
            add_cache_cmds.append(['set',
                                   self.cache_picker.pick_key(key),
                                   self.cache_picker.pick_value(value),
                                   self.ceche_timeout])
            miss_cache_dic[key] = value

        results = self.redis_client.pipe_execute(add_cache_cmds) if add_cache_cmds else []
        assert_redis_true(add_cache_cmds, results)

        # return to client
        return [cache_ls[i] if cache_ls[i] is not None else miss_cache_dic[k]
                for i, k in enumerate(keys)]

    def del_ls(self, keys):
        """
        同时删除storage和缓存的数据
        :param keys:
        :return: [value,,,]
        """
        if not keys:
            return
        results = self.redis_client.pipe_execute([['del', self.cache_picker.pick_key(key)] for key in keys])
        assert_redis_true(keys, results)

        self.storage_operator.del_ls(keys)
