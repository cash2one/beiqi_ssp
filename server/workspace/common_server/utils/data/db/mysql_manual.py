#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-26

@author: Jay
"""
import types
import datetime
import MySQLdb
from DBUtils.PooledDB import PooledDB
from MySQLdb.cursors import DictCursor, Cursor
from utils.comm_func import strip_dic_list
from utils.scheduler import Jobs
from utils.meta.instance_pool import InstancePool


class NoPool(object):
        def __init__(self, db_cnf_ins):
            self.conn = db_cnf_ins.get_conn()
            self.close = self.conn.close
            self.conn.close = lambda * arg: None

        def connection(self):
            return self.conn


# 如果一个客户端连接在8小时没有任何处理，数据库服务器将断开该连接
# 定时发起select 1维持连接的间隔，秒数,
SELECT_1_INTERVAL = 3600

class DbConnection(object):
    ATTR_DEFAULT_LST = [('db_host', '127.0.0.1'),
                        ('db_port', 3306),
                        ('db_name', ''),
                        ('db_username', ''),
                        ('db_password', ''),
                        ('use_pool', True),
                        ('min_cached', 1),
                        ('max_cached', 20),
                        ('max_shared', 1),
                        ('max_connections', 0),
                        ('blocking', False),
                        ('max_usage', None),
                        ('set_session', None),
                        ('reset', False),
                        ('failures', None),
                        ('ping', 1),
                        ('time_out', 2073600),
                        ('dict_cursor', True),
                        ('err_file', None),
                        ]

    # 是否使用连接池 use_pool 发布的服务器一开始可能没多少人玩 还是开启pool 后期可以考虑定期ping的形式而不用连接池 使用连接池带来的性能损耗是比较大的
    def __init__(self, **kwarg):
        for attr, default in self.ATTR_DEFAULT_LST:
            if attr not in kwarg:
                self.__dict__[attr] = default
            else:
                self.__dict__[attr] = kwarg[attr]

        self._conn = None
        self._pool = None

        # 间断select1 维持连接，不让数据库服务器给断开
        Jobs().add_interval_job(SELECT_1_INTERVAL, self.read_db, "select 1")

    def get_conn(self):
        if self._conn:return self._conn
        use_cursor = self.dict_cursor and DictCursor or Cursor
        self._conn = MySQLdb.connect(host=self.db_host,
                                     port=self.db_port,
                                     user=self.db_username,
                                     passwd=self.db_password,
                                     db=self.db_name,
                                     use_unicode=True,
                                     charset='utf8',
                                     cursorclass=use_cursor)

        # 设置当前连接超时时间 单位分钟 主要是db服务器改时间 可以造成连接过期
        cursor = self._conn.cursor()
        cursor.execute("set interactive_timeout=%s;" % self.time_out)
        cursor.execute("set wait_timeout=%s;" % self.time_out)
        cursor.close()
        return self._conn

    def get_connection(self):
        if not self._pool:
            self._create_pool()
        return self._pool.connection()

    def _create_pool(self):
        if self.use_pool:
            use_cursor = self.dict_cursor and DictCursor or Cursor
            self._pool = PooledDB(MySQLdb,
                                  mincached=self.min_cached,
                                  maxcached=self.max_cached,
                                  maxshared=self.max_shared,
                                  maxconnections=self.max_connections,
                                  blocking=self.blocking,
                                  maxusage=self.max_usage,
                                  setsession=self.set_session,
                                  reset=self.reset,
                                  failures=self.failures,
                                  ping=self.ping,
                                  host=self.db_host,
                                  port=self.db_port,
                                  user=self.db_username,
                                  passwd=self.db_password,
                                  db=self.db_name,
                                  use_unicode=True,
                                  charset='utf8',
                                  cursorclass=use_cursor)
        else:
            self._pool = NoPool(self)

    def get_pool(self):
        if not self._pool:
            self._create_pool()
        return self._pool

    def read_db(self, sql):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(sql)
        ret = cur.fetchall()
        cur.close()
        conn.commit()
        conn.close()
        return ret

    def write_db(self, sql_set):
        """
        写接口 不需返回ID(可以对多表操作)
        @param sql_set: SQL语句集合
        """
        # 从连接池获取一个连接
        conn = self.get_connection()
        cur = conn.cursor()
        is_success = False
        try:
            if isinstance(sql_set, types.ListType):
                # 多条语句
                for sql in sql_set:
                    cur.execute(sql)

            elif type(sql_set) in types.StringTypes:
                # 单条语句
                cur.execute(sql_set)

        except Exception, e:
            self.record_err(sql_set, e)
            conn.rollback()
            cur.close()
            conn.close()
            raise

        else:
            conn.commit()
            cur.close()
            conn.close()
            is_success = True
        return is_success

    def write_db_return_last_id(self, sql_set):
        """
        单写并返回ID
        """
        # 从连接池获取一个连接
        conn = self.get_connection()
        cur = conn.cursor()

        sucess = True
        try:
            if isinstance(type(sql_set), types.ListType):
                return

            elif type(sql_set) in types.StringTypes:
                # 单条语句
                cur.execute(sql_set)

        except Exception, e:
            self.record_err(sql_set, e)
            conn.rollback()
            cur.close()
            conn.close()
            raise
        else:
            conn.commit()
            cur.close()
            conn.close()

        last_id = cur.lastrowid if sucess else -1
        return last_id

    def multi_write_db(self, sql, param):
        """
        写接口, 对同一个表操作多条记录, 不需返回ID
        @param sql: 要操作的SQL格式(sql = 'INSERT INTO t2(money, gold) VALUES(%s, %s)')
        @param param: List or Tuple(param = [(100, 1000), (200, 2000)])
        """
        # 从连接池获取一个连接
        conn = self.get_connection()

        cur = conn.cursor()
        sucess = True
        if type(param) not in [types.ListType, types.TupleType]:
            param = [param]
        try:
            cur.executemany(sql, param)

        except Exception, e:
            self.record_err(sql, e, 'with par %s' % str(param))
            conn.rollback()
            cur.close()
            conn.close()
            raise

        else:
            conn.commit()
            cur.close()
            conn.close()
        last_id = cur.lastrowid if sucess else -1
        return last_id

    def multile_write_db_return_last_id(self, sql_set):
        """
        多写并返回ID集合(对同个表的操作)
        @param sql_set:
        """
        conn = self.get_connection()

        cur = conn.cursor()

        last_insert_id_list = []

        try:
            if isinstance(type(sql_set), types.ListType):
                return
            # 多条语句
            for sql in sql_set:
                cur.execute(sql)

                last_insert_id_list.append(cur.lastrowid)

        except Exception, e:
            self.record_err(sql, e)
            conn.rollback()
            cur.close()
            conn.close()
            raise

        else:
            conn.commit()
            cur.close()
            conn.close()
        return last_insert_id_list

    def record_err(self, sql, e, other_msg=''):
        self.err_file('[%s]: sql (%s)\n [error] %s | msg(%s) other(%s)\n' %
                      (datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"), sql, str(e), e.message, other_msg))

    def call_store_procs(self, store_procs_name, args):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.callproc(store_procs_name, args)
        result_set = cursor.fetchall()
        cursor.close()
        conn.commit()
        conn.close()
        return result_set


class DBInstance(object):
    def __init__(self, **kwargs):
        self.db_kwargs = kwargs
        self.base_db_ins = None
        self.user_db_ins = None
        self.schema_db_ins = None

    def __str__(self):
        return "%s:%s" % (self.db_kwargs['db_host'],self.db_kwargs['db_port'])

    def init(self):
        self.user_db_ins = DbConnection(**self.db_kwargs)
        self.db_kwargs.update({"db_name": "information_schema"})
        self.schema_db_ins = DbConnection(**self.db_kwargs)

    def read_schema(self, sql):
        return self.schema_db_ins.read_db(sql)

    def read_db(self, sql):
        return self.user_db_ins.read_db(sql)

    def get_userdb_connection(self):
        return self.user_db_ins.get_connection()

    def get_userdb_connins(self):
        return self.user_db_ins

    def write_db(self, sql_set):
        return self.user_db_ins.write_db(sql_set)

    def write_db_return_last_id(self, sql_set):
        return self.user_db_ins.write_db_return_last_id(sql_set)

    def multi_write_db(self, sql, param):
        return self.user_db_ins.multi_write_db(sql, param)

    def multile_write_db_return_last_id(self, sql_set):
        return self.user_db_ins.multile_write_db_return_last_id(sql_set)

    def get_userdb_pool(self):
        return self.user_db_ins.get_pool()

    def call_store_procs(self, store_procs_name, args):
        return self.user_db_ins.call_store_procs(store_procs_name, args)


def is_db_string(data_type):
    return data_type in ['text', 'varchar', 'char', 'date', 'datetime', 'tinytext', 'longtext']

class SchemaTable(object):
    __metaclass__ = InstancePool

    def __init__(self, db_instance, table_schema, table_name):
        assert isinstance(db_instance, DBInstance)
        self.db_instance = db_instance
        self.table_schema = table_schema
        self.table_name = table_name

        filed_info_sql = 'SELECT COLUMN_NAME,DATA_TYPE,COLUMN_DEFAULT FROM COLUMNS WHERE TABLE_SCHEMA = "%s" AND TABLE_NAME ="%s" '\
                         % (self.table_schema, self.table_name)
        field_info_ls = self.db_instance.read_schema(filed_info_sql)

        key_info_sql = """SELECT COLUMN_NAME FROM KEY_COLUMN_USAGE WHERE TABLE_NAME="%s" AND TABLE_SCHEMA="%s" LIMIT 1""" % (self.table_name, self.table_schema)
        key_info_ls = self.db_instance.read_schema(key_info_sql)
        self.key_field = key_info_ls[0]['COLUMN_NAME'] if key_info_ls else None

        self.field_info_dic = dict(((field_info['COLUMN_NAME'], field_info) for field_info in field_info_ls))
        self.fields = self.field_info_dic.keys()
        self.fields_str = ','.join(self.fields)

    def __make_sql_full_values(self, data_ls):
        if not data_ls:
            return

        strip_dic_list(data_ls)

        values_ls = []
        for data in data_ls:
            values = []

            for field in self.fields:
                field_info = self.field_info_dic[field]
                info = data.get(field_info['COLUMN_NAME'], field_info['COLUMN_DEFAULT'])
                if is_db_string(field_info['DATA_TYPE']):
                    if not str(info) or str(info) == 'None':
                        info = ''
                    values.append("'" + MySQLdb.escape_string(str(info)) + "'")
                else:
                    if not info:
                        info = 0
                    values.append(str(info))
            values_ls.append('(' + ','.join(values) + ')')
        return values_ls

    def __make_update_sqls(self, data_ls):
        if not data_ls:
            return

        strip_dic_list(data_ls)

        values_ls = []
        for data in data_ls:
            assert self.key_field in data

            set_str_ls = []
            for field, value in data.items():
                if field not in self.field_info_dic:
                    continue

                field_info = self.field_info_dic[field]

                if field == self.key_field:
                    continue

                if is_db_string(field_info['DATA_TYPE']):
                    set_str_ls.append('%s=\'%s\'' % (field, MySQLdb.escape_string(str(value))))
                else:
                    set_str_ls.append('%s=%s' % (field, value))

            kft = self.field_info_dic[self.key_field]['DATA_TYPE']
            key_str = ('%s=\'%s\'' if kft else '%s=%d') % (self.key_field, MySQLdb.escape_string(str(data[self.key_field])))
            set_str = ','.join(set_str_ls)
            values_ls.append('UPDATE %s SET %s WHERE %s' % (self.table_name, set_str, key_str))
        return values_ls

    def __make_delete_sql(self, data_ls):
        if not data_ls:
            return

        strip_dic_list(data_ls)

        sql = "delete from " + self.table_name + " where "

        for idx, data in enumerate(data_ls):
            assert self.key_field in data

            kft = self.field_info_dic[self.key_field]['DATA_TYPE']
            key_str = ('%s=\'%s\'' if kft else '%s=%d') % (self.key_field, MySQLdb.escape_string(str(data[self.key_field])))
            sql += "%s" % key_str if idx == 0 else "OR %s" % key_str
        return sql

    def __get_db_data(self, data):
        """
        获取数据列表里面的有效数据库字段数据
        :param data:
        :return:data
        """
        if not data:
            return {}

        data = dict((field, value) for field, value in data.items() if field in self.field_info_dic)
        return data

    def insert_ls(self, data_ls):
        if not data_ls:
            return

        values_ls = self.__make_sql_full_values(data_ls)
        assert values_ls

        sql = 'insert into %s(%s) values %s' % (self.table_name, self.fields_str, ','.join(values_ls))
        return self.db_instance.write_db_return_last_id(sql)

    def delete_ls(self, data_ls):
        if not data_ls:
            return

        sql = self.__make_delete_sql(data_ls)
        assert sql
        return self.db_instance.read_db(sql)

    def query_all(self):
        sql = "select * from " + self.table_name
        data_ls = self.db_instance.read_db(sql)
        strip_dic_list(data_ls)
        return data_ls

    def query(self, sql):
        data_ls = self.db_instance.read_db(sql)
        strip_dic_list(data_ls)
        return data_ls

    def replace_ls(self, data_ls):
        if not data_ls:
            return

        values_ls = self.__make_sql_full_values(data_ls)
        assert values_ls

        sql = 'replace into %s(%s) values %s' % (self.table_name, self.fields_str, ','.join(values_ls))
        return self.db_instance.write_db(sql)

    def update_ls(self, data_ls):
        if not data_ls:
            return

        update_sqls = self.__make_update_sqls(data_ls)
        assert update_sqls
        return self.db_instance.write_db(update_sqls)

    def update_diff(self, old_data_ls, new_data_ls):
        """
        比较不同版本数据，并更新
        :param old_data_ls:老数据
        :param new_data_ls: 新数据
        :return:None
        """
        if not old_data_ls and not new_data_ls:
            return

        # 统一转成unicode dict
        old_data_dic = dict((unicode(dic[self.key_field]), dict((unicode(k), unicode(v)) for k, v in dic.items()))
                            for dic in old_data_ls)
        new_data_dic = dict((unicode(dic[self.key_field]), dict((unicode(k), unicode(v)) for k, v in dic.items()))
                            for dic in new_data_ls)

        # insert
        insert_keys = set(new_data_dic.keys()).difference(set(old_data_dic.keys()))
        insert_data_ls = [new_data_dic[key] for key in insert_keys]
        insert_data_ls = self.__make_sql_full_values(insert_data_ls)
        insert_mysql = 'insert into %s(%s) values %s' % (self.table_name, self.fields_str, ','.join(insert_data_ls)) \
            if insert_data_ls \
            else None

        # delete
        delete_keys = set(old_data_dic.keys()).difference((new_data_dic.keys()))
        delete_data_ls = [old_data_dic[key] for key in delete_keys]
        delete_mysql = self.__make_delete_sql(delete_data_ls) if delete_data_ls else None

        # update
        update_keys = [key for key in set(new_data_dic.keys()).intersection(set(old_data_dic.keys()))
                       if self.__get_db_data(old_data_dic[key]) != self.__get_db_data(new_data_dic[key])]
        update_data_ls = [new_data_dic[key] for key in update_keys]
        update_mysqls = self.__make_update_sqls(update_data_ls) if update_data_ls else None

        # run mysql
        sqls = []
        sqls.append(insert_mysql) if insert_mysql else None
        sqls.append(delete_mysql) if delete_mysql else None
        sqls.extend(update_mysqls) if update_mysqls else None
        return self.db_instance.write_db(sqls)

