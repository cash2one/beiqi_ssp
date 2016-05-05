#coding:utf-8


import re
from os import path
from convert import iter_file
from functools import partial
from re_ex import reg_sub_ex
from types import GeneratorType
from cStringIO import StringIO
from contextlib import contextmanager


SECTION_PATTERN = re.compile(r'^\[(?P<sec>.*)\]')
FIELD_PATTERN = re.compile(r'^(?P<key>[_a-zA-Z\d\.]+)\s*=\s*(?P<value>.*?)(?=\s+[;#]|$)')
user_pat = re.compile(r'~')
#同样，只支持_或者ascii字母开头的变量
var_pat = re.compile(r'\$(?P<name>[_a-zA-Z][_\-a-zA-Z\d]*)')
curuser = path.expanduser(user_pat.pattern)


def _match_user(m):
    """
    扩展~到当前用户
    """
    return curuser


def _parse(iter_line):
    cur_sec = None
    result = {}
    for l in iter_line:
        if l.startswith('#') or l.startswith(';'):
            continue
        m = SECTION_PATTERN.search(l)
        if m:
            if result:
                yield result
            cur_sec = m.groupdict().get('sec')
            result = {cur_sec: {}}
        else:
            if not cur_sec:
                raise ValueError('no section wrap')
            m = FIELD_PATTERN.search(l)
            if not m:
                raise ValueError('field invalid: {0}'.format(l))
            result[cur_sec].update(
                {
                    m.groupdict().get('key'): m.groupdict().get('value')
                }
            )
    if result:
        yield result


def conf_file(fn):
    """
    从文件创建配置对象
    """
    if not (fn and path.exists(fn)):
        raise ValueError('conf {0} not found'.format(fn))
    return ConfigX(iter_file(fn))


@contextmanager
def _stream_helper(s):
    """
    保证外部对config对象的调用方式一致
    """
    io = StringIO(s)
    yield ConfigX((x.strip() for x in io.readlines() if x.strip()))
    io.close()


def conf_stream(s):
    """
    从网络流创建配置对象
    :param s: 网络字节流
    """
    with _stream_helper(s) as o:
        return o


class ConfigX(object):
    """
    ini文件格式解析
    """
    def __init__(self, iter_src):
        """
        :param iter_src: 文件行迭代器
        """
        if not (iter_src and isinstance(iter_src, GeneratorType)):
            raise ValueError('iter_src invalid')

        self.__d = {}
        for x in _parse(iter_src):
            self.__d.update(x)

        self.__cache = {}
        for s in self.get_sections():
            if s not in self.__cache:
                self.__cache.update({s: {}})
            for f, v in self.get_fields(s).iteritems():
                self.__cache[s].update({f: v})

    def __match_field(self, m, dest_key=None):
        """
        匹配已有键值，不区分section
        """
        key = m.groupdict().get('name')
        if dest_key and key == dest_key:
            raise ValueError('recursion key %r' % key)

        for v in self.__cache.itervalues():
            if key not in v:
                continue
            return v.get(key)
        raise ValueError('key %r not found' % key)

    def get_resolve(self, section, key):
        """
        对于$开头的字符串，会解引用
        对于~字符，解析到当前用户目录
        """
        v = self.get(section, key)
        if v is None:
            return v
        match_raw_dest = partial(self.__match_field, dest_key=key)
        return reg_sub_ex(user_pat, reg_sub_ex(var_pat, v, match_raw_dest), _match_user)

    def get(self, section, key, _type=None):
        """
        读取键值
        :param section:
        :param key:
        :param _type:
        :return:
        """
        v = self.__d.get(section)
        if not v:
            return None
        if not _type:
            return v.get(key)
        return _type(v.get(key))

    def get_fields(self, section):
        """
        获取section下属的所有fields
        :param section:
        :return:
        """
        return self.__d.get(section)

    def has_section(self, section):
        """
        是否存在section
        :param section:
        :return:
        """
        return section in self.__d

    def get_sections(self):
        """
        返回所有section
        :return:
        """
        return self.__d.iterkeys()
