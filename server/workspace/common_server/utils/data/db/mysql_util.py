#coding:utf-8
"""
Created on 2014年11月10日

@author: jay
"""
# 查找utils
import site, os
site.addsitedir(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
import platform
import time
from mysql_manual import DBInstance
from gevent import subprocess
from utils.wapper.stackless import gevent_adaptor
from utils.comm_func import timestamp_to_format_string


class MysqlUtil:
    """
    Mysql操作接口
    """
    @staticmethod
    def check_db_exist(dbip,dbport,dbuser,dbpass,dbname):
        """
        检查数据库表是否存在
        @param dbip:待检查数据库ip
        @param dbport:待检查数据库端口
        @param dbuser:待检查数据库用户
        @param dbpass:待检查数据库密码
        @param dbname:待检查数据库表
        """
        schema_db_conn=DBInstance(db_host=dbip, db_port=dbport, db_name='information_schema', db_username=dbuser, db_password=dbpass)
        schema_db_conn.init()

        sql = "SELECT SCHEMA_NAME FROM SCHEMATA where SCHEMA_NAME = '%s'"%dbname
        ret = schema_db_conn.read_schema(sql)
        return ret

    @staticmethod
    def create_db(dbip,dbport,dbuser,dbpass,dbname):
        """
        创建用户数据库
        @param dbip:待创建数据库ip
        @param dbport:待创建数据库端口
        @param dbuser:待创建数据库用户
        @param dbpass:待创建数据库密码
        @param dbname:待创建数据库表
        """
        schema_db_conn=DBInstance(db_host=dbip, db_port=dbport, db_name='information_schema', db_username=dbuser, db_password=dbpass)
        schema_db_conn.init()

        sql = 'create database if not exists %s CHARACTER SET utf8 '%dbname
        schema_db_conn.read_schema(sql)
        return MysqlUtil.check_db_exist(dbip, dbport, dbuser, dbpass, dbname)

    @staticmethod
    @gevent_adaptor()
    def db_dump(src_dbip,src_dbport,src_dbuser,src_dbpass,src_dbname,des_path=None,use_gzip=True):
        """
        数据库备份
        @param src_dbip:备份数据库ip
        @param src_dbport:备份数据库端口
        @param src_dbuser:备份数据库用户
        @param src_dbpass:备份数据库密码
        @param src_dbname:备份数据库表
        @param des_path:备份文件存放地址
        @param use_gzip:是否使用gzip压缩数据,默认是
        """
        # 如果目标路径存在，判断目录是否存在
        if des_path:
            dir_flag = "/" if platform.system() == 'Linux' else '\\'
            des_dir = des_path[0:des_path.rfind(dir_flag)]
            if not os.path.exists(des_dir):
                os.makedirs(des_dir)

        # 如果目标路径不存在，创建路径
        else:
            # sql dump 目录
            if platform.system() == 'Linux':
                SQL_DUMP_DIR = '/home/sqldump/'
            else:
                SQL_DUMP_DIR = 'C:\\sqldump\\'
            if not os.path.exists(SQL_DUMP_DIR):
                os.makedirs(SQL_DUMP_DIR)

            # 临时备份文件
            des_path = ("%s%s_%s.sql") % (SQL_DUMP_DIR, src_dbname, timestamp_to_format_string(time.time(), "%Y_%m_%d_%H_%M_%S"))
            des_path += ".gz" if use_gzip else ""

        if use_gzip:
            mysqldump_cmd = "mysqldump -h%s -u%s -p%s -P %s --single-transaction %s|gzip >%s"%(src_dbip,src_dbuser,src_dbpass,src_dbport,src_dbname,des_path)
        else:
            mysqldump_cmd = "mysqldump -h%s -u%s -p%s -P %s --single-transaction %s >%s"%(src_dbip,src_dbuser,src_dbpass,src_dbport,src_dbname,des_path)
        _, stderr = subprocess.Popen(mysqldump_cmd,stderr=subprocess.PIPE, shell = True).communicate()
        assert not stderr,stderr

    @staticmethod
    @gevent_adaptor()
    def db_import(src_path,des_dbip,des_dbport,des_dbuser,des_dbpass,des_dbname,use_gzip=True):
        """
        数据库import操作
        @param src_path:import路径
        @param des_dbip:备份数据库ip
        @param des_dbport:备份数据库端口
        @param des_dbuser:备份数据库用户
        @param des_dbpass:备份数据库密码
        @param des_dbname:备份数据库表
        @param use_gzip:是否使用gzip压缩数据,默认是
        """
        # create db
        if not MysqlUtil.check_db_exist(des_dbip, des_dbport, des_dbuser, des_dbpass, des_dbname):
            assert MysqlUtil.create_db(des_dbip, des_dbport, des_dbuser, des_dbpass, des_dbname)

        # gzip 解压缩
        if use_gzip:
            import_cmd = "gunzip < %s | mysql -h%s -P%s -u%s -p%s %s"%(src_path,des_dbip,des_dbport,des_dbuser,des_dbpass,des_dbname)
        else:
            import_cmd = "mysql -h%s -P%s -u%s -p%s %s < %s"%(des_dbip,des_dbport,des_dbuser,des_dbpass,des_dbname,src_path)
        _, stderr = subprocess.Popen(import_cmd,stderr=subprocess.PIPE, shell = True).communicate()
        assert not stderr,stderr

    @staticmethod
    @gevent_adaptor()
    def db_move(src_dbip,src_dbport,src_dbuser,src_dbpass,src_dbname,
                des_dbip,des_dbport,des_dbuser,des_dbpass,des_dbname=None):
        """
        数据库表移动
        :param src_dbip: 源dbip
        :param src_dbport: 源db端口
        :param src_dbuser: 源db用户
        :param src_dbpass: 源db密码
        :param src_dbname: 源db表格
        :param des_dbip:   目标dbip
        :param des_dbport: 目标db端口
        :param des_dbuser: 目标db用户
        :param des_dbpass: 目标db密码
        :param des_dbname: 目标db表格，如果为空的，就和src_dbname一只
        :return: None
        """
        # sql dump 目录
        if platform.system() == 'Linux':
            SQL_DUMP_DIR = '/home/sqldump/'
        else:
            SQL_DUMP_DIR = 'C:\\sqldump\\'
        if not os.path.exists(SQL_DUMP_DIR):
            os.makedirs(SQL_DUMP_DIR)

        # 是否使用gzip
        use_gzip = 1 if platform.system() == 'Linux' else 0

        # 临时备份文件
        dump_file = ("%s%s_%s.sql") % (SQL_DUMP_DIR, src_dbname, time.time())
        dump_file += ".gz" if use_gzip else ""

        # 目的db表格
        if not des_dbname:
            des_dbname = src_dbname

        MysqlUtil.db_dump(src_dbip, src_dbport, src_dbuser, src_dbpass, src_dbname, dump_file, use_gzip)
        MysqlUtil.db_import(dump_file, des_dbip, des_dbport, des_dbuser, des_dbpass, des_dbname, use_gzip)