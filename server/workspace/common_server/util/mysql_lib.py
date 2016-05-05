#coding:utf-8


from sql_expr import exec_sql
from stream_config_client import load as conf_load
import torndb
from cPickle import dumps as mysql_dump, loads as mysql_load
import struct
from os import remove, path
from convert import mongo2utf8


__all__ = ['export_tool', 'import_tool']
cms_conf = dict(conf_load('mysql.ini')).get('mysql.ini')


def _export(query_sql, insert_rec, *query_params):
    """
    导出mysql指定数据库，指定记录到文件
    :param query_sql:
    :param insert_rec: 插入记录
    :param query_params: 查询参数
    """
    insert_rec = insert_rec or {}
    mysql_db = torndb.Connection(**cms_conf.get_fields('cms'))
    recs = mysql_db.query(query_sql, *query_params)

    for l in recs:
        l.update(insert_rec)
        yield l


def _dump(iter_recs, out_fn):
    """
    写入记录, 使用pickle格式
    :param iter_recs:
    :param out_fn:
    """
    fd = open(out_fn, 'wb')
    try:
        for r in iter_recs:
            buf = mysql_dump(r)
            fd.write('{0}{1}'.format(struct.pack('>H', len(buf)), buf))
    except Exception, ex:
        fd.close()
        remove(out_fn)
        print ex
    else:
        fd.close()


def _load(mysql_export_fn, null_field_func):
    """
    载入文件
    :param mysql_export_fn:
    :param null_field_func: null字段默认赋值
    """
    with open(mysql_export_fn, 'rb') as fd:
        while 1:
            #read同时，指针会向前移动
            seek = fd.read(2)
            if not seek:
                break
            seek = struct.unpack('>H', seek)[0]
            _ = mysql_load(fd.read(seek))
            yield _ if not null_field_func else null_field_func(_)


def _import(table, obs, *time_fields):
    mysql_db = torndb.Connection(**cms_conf.get_fields('cms'))
    for o in obs:
        o = mongo2utf8(o)
        exec_sql(mysql_db, table, o, 0, None, *time_fields)


def export_tool(query_sql, insert_rec, out_fn, *query_args):
    """
    导出
    :param query_sql:
    :param insert_rec:
    :param out_fn:
    """
    _dump(_export(query_sql, insert_rec, *query_args), out_fn)


def import_tool(table_name, mysql_export_fn, null_field_func=None, *time_fields):
    """
    导入数据
    :param table_name:
    :param mysql_export_fn:
    """
    if not path.isfile(mysql_export_fn):
        return
    _import(table_name, _load(mysql_export_fn, null_field_func), *time_fields)