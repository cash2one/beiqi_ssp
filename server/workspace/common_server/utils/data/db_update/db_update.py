# coding=utf-8
"""
Created on 2015-4-22

@author: Jay
"""
import logging
import os
import MySQLdb
from utils.data.db_update.table_reader import *
from utils import logger


class DBVersion(Record):

    _fields_ = [('version', c_int),             # 版本号
                ('file_path', c_char*50),       # 文件夹名字
                ]


class UpdataDB():
    
    def __init__(self, db_host, db_port, db_name, db_user, db_pw, file_path):
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_pw = db_pw
        self.file_path = file_path
        # 数据库版本记录表
        self.db_version_table = TableData(os.path.join(self.file_path, "db_version.txt"), DBVersion, ['version'])
        # 初始化数据结构的文件路径
        self.db_init_file = os.path.join(self.file_path, "init_db.sql")
        
        self.db_version = 0
        
    def check_db_exist(self):
        """
        检查用户数据库是否存在
        """
        sql = "SELECT SCHEMA_NAME FROM SCHEMATA where SCHEMA_NAME = '%s'" % self.db_name
        conn = MySQLdb.connect(host=self.db_host,
                               port=self.db_port,
                               user=self.db_user,
                               passwd=self.db_pw,
                               db='information_schema')
        cursor = conn.cursor()
        cursor.execute(sql)
        ret = cursor.fetchall()
            
        cursor.close()
        conn.commit()
        conn.close()
        
        return bool(len(ret) > 0)
    
    def create_db(self):
        """
        创建用户数据库
        """
        sql = 'create database if not exists %s CHARACTER SET utf8 COLLATE utf8_bin' % self.db_name
        conn = MySQLdb.connect(host=self.db_host,
                               port=self.db_port,
                               user=self.db_user,
                               passwd=self.db_pw,
                               db='information_schema')
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
        except Exception, e:
            print sql, e
            return False
        
        cursor.close()
        conn.close()
        return True
    
    def init_db_data(self):
        """
        初始化数据库
        """
        if not os.path.isfile(self.db_init_file):
            return False
        if self.db_exec_file(self.db_init_file):
            return True
        
    def db_exec_file(self, file_path):
        """
        数据库执行sql文件
        @param file_path:文件路径
        """
        file_path = file_path.replace("\\", "/")
        if not os.path.exists(file_path):
            return False
        st = 'mysql -h %s -P%s -u%s -p%s %s < %s' % (self.db_host, self.db_port, self.db_user, self.db_pw, self.db_name, file_path)
        res = os.system(st)
        if res == 0:
            logger.info(' <db:%s> successful exec sql file = %s', self.db_name, file_path)
            return True
        else:
            logger.error("error when exec command '%s'! ", st)
            return False

    def db_update_version(self, tar_version):
        """
        更新用户数据库的版本
        @param tar_version:目标版本 
        """
        if not self.check_db_exist():
            if not self.create_db():    # 创建数据库
                logging.error("fail to create db!")
                return False
            if not self.init_db_data():   # 初始化数据库结构和数据
                logging.error("fail to init db!")
                return False
        # 当前数据库的版本
        cur_db_version = self.get_cur_db_version()
        
        # 没有版本变更
        if self.db_version_table.get_count() <= 0:
            logging.info("not version to update!")
            return True
        
        if not tar_version:
            tar_version = self.db_version_table.get_last_record().version
            
        for version in xrange(cur_db_version + 1, tar_version + 1):
            version_record = self.db_version_table.get_record_by_mainkeylst(version)
            if not version_record:
                logging.error('db version = %s not be found in db_version.txt', version)
                return False
            file_path = os.path.join(self.file_path, "DBVersion", version_record.file_path)
            if not os.path.isfile(file_path):
                logging.error("not find database file! file name = %s" % file_path)
                return False
            if not self.db_exec_file(file_path):
                logging.error("fail to exec mysql sql! file path = %s" % file_path)
                return False
            if not self.set_cur_db_version(version):
                logging.error("fail to set current version = %s" % version)
                return 
            logging.info('update db to version = %s successful!', version)
            
        return True
    
    def get_cur_db_version(self):
        """
        获得数据库版本
        """
        if self.db_version > 0:
            return self.db_version
        
        sql_cmd = 'select db_version from db_version'
        ret = self.__db_exec_read(sql_cmd)
        if len(ret) <= 0:
            return -1
        self.db_version = ret[0][0]
        return self.db_version
    
    def set_cur_db_version(self, db_version):
        """
        设置数据库的版本
        :param db_version:
        """
        sql_cmd = "update db_version set db_version = %s" % db_version
        ret = self.__db_exec_write(sql_cmd)
        if ret:
            self.db_version = db_version
            return True

    def __db_exec_read(self, sql_cmd):
        """
        用户数据库执行读操作
        @param sql_cmd:
        """
        conn = MySQLdb.connect(host=self.db_host,
                               port=self.db_port,
                               user=self.db_user,
                               passwd=self.db_pw,
                               db=self.db_name)
        cur = conn.cursor()
        cur.execute(sql_cmd)
        ret = cur.fetchall()
        cur.close()
        conn.close()
        return ret
    
    def __db_exec_write(self, sql_cmd):
        """
        用户数据库执行写操作
        @param sql_cmd:
        """
        conn = MySQLdb.connect(host=self.db_host,
                               port=self.db_port,
                               user=self.db_user,
                               passwd=self.db_pw,
                               db=self.db_name)
        cur = conn.cursor()
        try:
            cur.execute(sql_cmd)
             
        except Exception, e:
            print sql_cmd, e
            conn.rollback()
        else:
            conn.commit()
        cur.close()
        conn.close()
        return True
        
db_update_obj = None


def get_db_update_obj(db_host, db_port, db_name, db_user, db_pw, file_path):
    global db_update_obj
    
    if not db_update_obj:
        db_update_obj = UpdataDB(db_host, db_port, db_name, db_user, db_pw, file_path)
    return db_update_obj


def main(db_host, db_port, db_name, db_user, db_pw, file_path="", no=0):
    return get_db_update_obj(db_host, db_port, db_name, db_user, db_pw, file_path).db_update_version(no)
     
if __name__ == '__main__':
    while True:
        no = raw_input('player input user db target version:')
        if not no or no.isdigit():
            main("192.168.1.121", 3306, "gs1", "system", "system")
            break
