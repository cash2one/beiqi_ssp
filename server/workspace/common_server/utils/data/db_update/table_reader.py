# coding=utf-8
"""
Created on 2015-4-22

@author: Jay
"""
from ctypes import *
import types

OUTPUT_SINGLE_SPACE = 15


class Record(Structure):
    """
    表中的单条记录类 紧凑结构 note:
    如果table字段超长的话这里会报错 需要注意 开服是注意 发现报错修改表 或者让程序修改字段长度
    """
    _fields_ = []
    _char_to_lst_ = []
    _char_to_eval_ = []
    _char_to_compile_ = []

    # 空串代替符
    NULL_CHAR = '-'

    # _char_to_lst_ 分割符
    SPLITE_CHAR = ','

    def __init__(self):
        self.keys = set([])
        self.lenth = len(self._fields_)

    def readdata(self, line):
        datalst = [i.strip() for i in line.strip().split('\t')]

        for fieldindex, data in enumerate(datalst[:self.lenth]):
            attr_name, attr_type = self._fields_[fieldindex]
            self.keys.add(attr_name)
            if attr_type in [c_short, c_ushort, c_int, c_uint, c_long,
                             c_ulong, c_longlong, c_ulonglong, c_ubyte, c_float, c_double]:
                # @note:  可以将一些 字段很长的 但是服务端不需要记录的数据
                # 类型字段设计成为c_int或其他上面的 这样这些字符串数据不会读到内存
                try:
                    data = eval(data)
                except:
                    data = 0
            else:
                # @warning: do something here if you want to prevent fields too long error
                pass

            try:
                setattr(self, attr_name, data)
            except:
                print data, line, fieldindex
                raise
        for src_key, dest_key in self._char_to_lst_:
            src_data = getattr(self, src_key, None)

            dest_value = []
            if src_data.strip() != self.NULL_CHAR:
                try:
                    replaced_data = src_data.replace(self.SPLITE_CHAR, ',')
                    dest_value = eval("[%s]" % replaced_data)
                except:
                    pass

            setattr(self, dest_key, dest_value)
            self.keys.add(dest_key)

        for src_key, dest_key in self._char_to_eval_:
            src_data = getattr(self, src_key, None)

            dest_value = None
            if src_data.strip() != self.NULL_CHAR:
                try:
                    dest_value = eval(src_data)
                except:
                    pass
            setattr(self, dest_key, dest_value)
            self.keys.add(dest_key)

        for src_key, dest_key in self._char_to_compile_:
            src_data = getattr(self, src_key, None)

            dest_value = None
            if src_data.strip() != self.NULL_CHAR:
                try:
                    dest_value = compile(src_data, '', 'eval')
                except:
                    pass

            setattr(self, dest_key, dest_value)
            self.keys.add(dest_key)

    def setdata(self, datalst):
        for fieldindex, data in enumerate(datalst):
            setattr(self, self._fields_[fieldindex][0], data)

    def get_data(self):
        data = {}
        for key, _ in self._fields_:
            data.update({key: getattr(self, key)})
        return data

    def __str__(self):
        """
        单条记录的str
        :return:
        """
        return ' '.join([(str(getattr(self, i[0]))
                          [:OUTPUT_SINGLE_SPACE].center(OUTPUT_SINGLE_SPACE)) for i in self._fields_]) + '\n'

    @staticmethod
    def get_header(cls):
        """
        类的头 的输出str 需要给定具体的类 子类。
        :param cls:
        :return:
        """
        return '|'.join([(str(i[0])
                          [:OUTPUT_SINGLE_SPACE].center(OUTPUT_SINGLE_SPACE)) for i in cls._fields_]) + '\n'

    @staticmethod
    def reload_update(oldobj, newobj):
        """
        用于reload
        @param oldobj:
        """
        return newobj

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        if not hasattr(self, key):
            return None
        return getattr(self, key)

    def get(self, key, default=None):
        if not hasattr(self, key):
            return default
        return getattr(self, key)

    def getkeys(self):
        return self.keys


class TableData(object):
    """
    表的数据 有每行数据构成 维护  索引  提供通过索引获得行
    通过index 获得行 获得行的总数 获得满足某些条件的行的列表等接口
    """
    def __init__(self,
                 filepath,
                 classname,
                 mainkeylist,
                 startline='#------------'):
        """
        建索引 读文件中的数据
        @param filepath 文件路径
        @param classname 类
        @param mainkeylist 主键列表
        @param startline 分隔符或起始行号
        """
        self.records = []
        self.main_key_data = {}   # 唯一的，只有一条数据
        self.index_dict = {}   # 索引字典，{'索引名称':索引字段名列表, ...}，同一个索引值可活动多条数据
        self.classname = classname
        pf = open(filepath, 'r')
        lines = pf.readlines()

        start_line = 0
        if type(startline) == int:
            start_line = startline
            started = True
        else:
            started = False
        cur_effect_index = 0
        for line_no, line in enumerate(lines):
            if not started:
                if line.startswith(startline):
                    started = True
                    start_line = line_no + 2
                continue
            else:
                if line_no < start_line:
                    continue

            line = line.strip()
            if not line:
                continue
            record = classname()
            record.readdata(line)
            index_key = [getattr(record, i) for i in mainkeylist]
            self.main_key_data[tuple(index_key)] = cur_effect_index
            cur_effect_index += 1
            self.records.append(record)
        pf.close()

    def add_index(self, index_name, fieldname_list):
        """
        添加索引
        :param index_name:
        :param fieldname_list:
        :return:
        """
        if index_name in self.index_dict:
            raise 'already exist index_name:%s' % index_name
        self.index_dict.setdefault(index_name, {})
        offset = 0
        for record in self.records:
            field_values = tuple([record[i] for i in fieldname_list])
            self.index_dict[index_name].setdefault(field_values, [])
            self.index_dict[index_name][field_values].append(offset)
            offset += 1

    def get_record(self, index_name, field_values):
        """
        根据索引名称和字段值列表，获取数据
        如果要查询的是主键，请使用get_record_by_mainkeylst
        :param index_name:
        :param field_values:
        :return:
        """
        if type(field_values) not in [types.ListType, types.TupleType]:
            field_values = [field_values]
        pos_list = self.index_dict.get(index_name, {}).get(tuple(field_values), [])
        ret = []
        for pos in pos_list:
            ret.append(self.get_record_by_index(pos))
        return ret

    def get_record_by_index(self, index):
        """
        根据位置获取记录
        :param index:
        :return:
        """
        assert index < len(self.records)
        return self.records[index]

    def get_record_by_mainkeylst(self, mainkeylst):
        """
        根据主键的值获得对应的数据 主键是一开始剪标的时候定的 如果需要支持多个索引的话需要在这改
        """
        if type(mainkeylst) not in [types.ListType, types.TupleType]:
            mainkeylst = [mainkeylst]
        getindex = self.main_key_data.get(tuple(mainkeylst))
        if getindex is not None:
            return self.get_record_by_index(getindex)

    def get_record_by_key(self, value):
        return self.records[self.main_key_data[(value, )]]

    def get_records_by_matchdict(self, matchdict, maxcount=999):
        """
        获得能够满足matchdict 给的键值和对应的值 找到满足条件的record 最多maxcount个 默认1000个
        :param matchdict:
        :param maxcount:
        :return:
        """
        reslst = []
        findcount = 0
        for record in self.records:
            match = True
            for key, value in matchdict.items():
                if getattr(record, key) != value:
                    match = False
                    break

            if match:
                findcount += 1
                reslst.append(record)
                if findcount >= maxcount:
                    break
        return reslst

    def __str__(self):
        """
        表的格式化输出
        :return:
        """
        headstr = self.classname.get_header(self.classname) + '—'*200+'\n'
        recordstr = ' '.join([str(i) for i in self.records])
        return ' %s %s\n' % (headstr, recordstr)

    def get_count(self):
        return len(self.records)

    def get_last_record(self):
        return self.get_record_by_index(self.get_count() - 1)

    def __iter__(self):
        for record in self.records:
            yield record

    def __len__(self):
        return len(self.records)

    def get_max_key(self, key_name):
        return max([getattr(record, key_name) for record in self.records])

    def get_min_key(self, key_name):
        return min([getattr(record, key_name) for record in self.records])

    def search_records(self, select_fieldnames, where_condition, limit_from=0, limit_to=0, is_like_search=False):
        """
        询表数据
        @param select_fieldnames:查询的字段名称列表
        @param where_condition:条件语句
        @param limit_from:限制条件，从第几条开始
        @param limit_to:限制条件，到第几条结束,如果limit_from和limit_to均为0，则返回所有数据
        @param is_like_search:是否进行模糊匹配
        :return:
        """
        find_records = []
        for record in self.records:
            keys = where_condition.keys()
            # 使用模糊查询
            is_find = True
            for key in keys:
                # 模糊匹配
                if is_like_search and where_condition[key] in record[key]:
                    continue
                # 完全匹配
                elif not is_like_search and where_condition[key] == record[key]:
                    continue
                is_find = False
                break

            if not is_find:
                continue
            find_record = {}
            for field_name in select_fieldnames:
                find_record[field_name] = record[field_name]
            find_records.append(find_record)
        if limit_from == 0 and limit_to == 0:
            return find_records
        return find_records[limit_from:limit_to]


class RecordEx(object):
    """
    PYTHON SLOTS 结构的类  考虑到有可能字段的可变性较大 不采用固定的 Struct
    """
    _fields_ = []
    __slots__ = []

    def __init__(self):
        fields_set = set(self._fields_)
        for var in self.__slots__:
            if var not in fields_set:
                setattr(self, var, None)

    def readdata(self, line):
        """
        读取数据 给定一行
        :param line:
        :return:
        """
        lenth = len(self._fields_)
        datalst = [i.strip() for i in line.strip().split('\t')]
        for fieldindex, data in enumerate(datalst[:lenth]):
            setattr(self, self._fields_[fieldindex], data)

    def __str__(self):
        """
        单条记录的str
        :return:
        """
        return ' '.join([(str(getattr(self, attr_name))
                          [:OUTPUT_SINGLE_SPACE].center(OUTPUT_SINGLE_SPACE)) for attr_name in self._fields_]) + '\n'

    @staticmethod
    def get_header(cls):
        """
        类的头 的输出str 需要给定具体的类 子类。
        :param cls:
        :return:
        """
        return ' '.join([(str(attr_name)
                          [:OUTPUT_SINGLE_SPACE].center(OUTPUT_SINGLE_SPACE)) for attr_name in cls._fields_]) + '\n'