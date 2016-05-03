# coding:utf-8
"""
Created on 2015年6月01日

@author: jay
"""
import logging
class DirtyFlag(object):
    """
    脏数据标志类
    """
    def __init__(self):
        self.all_flag_set = set([])
        self.dirty_flag_set = set([])

    def add_flag(self, k):
        self.all_flag_set.add(k)
        self.dirty_flag_set.add(k)
        
    def add_flag_set(self, k_set):
        self.all_flag_set.update(k_set)
        self.dirty_flag_set.update(k_set)
        
    def del_flag(self, k):
        self.all_flag_set.remove(k)
        self.dirty_flag_set.remove(k)
            
    def reset_flags(self, reset_value):
        if reset_value:
            self.dirty_flag_set.update(self.all_flag_set)
        else:
            self.dirty_flag_set.clear()
    
    def del_all_flag(self):
        self.dirty_flag_set.clear()
            
    def get_all_keys(self):
        """
        获取所有的keys
        """
        return self.all_flag_set
        
    def get_dirty_keys(self):
        """
        获取脏数据的keys
        """
        return self.dirty_flag_set


class DirtyFlagProcess(object):
    """
    脏字段处理类,本身不维护数据,需要提供一个数据源,然后和flag一一对应的key值
    """
    def __init__(self,data_father, keep_client_keys=[]):
        """
        类初始方法
        :param data_father:数据源
        :param keep_client_keys: 必须发给客户端的key
        """
        self.data_father = data_father
        self.keep_client_keys = keep_client_keys
        
        self.client_dirty_flag = DirtyFlag()    # 需要同步到客户端的脏数据
        self.db_dirty_flag = DirtyFlag()        # 需要保存到数据库的脏数据
        
        self.dirty_notify_fun_ls = []
        
    def __get_class_attr(self, k):
        return self.data_father.__dict__.get(k)
    
    def __notify_client_dirty(self):
        """
        把数据变脏的事实通知给指定的函数
        """
        for fun_info in self.dirty_notify_fun_ls:
            fun = fun_info[0]
            fun_args = fun_info[1]
            fun_kwargs = fun_info[2]
            fun(*fun_args, **fun_kwargs)
        
    def add_dirty_notify_fun(self, fun,*args, **kwargs):
        """
        增加脏数据callback函数
        :param fun:函数
        :param args:数组参数
        :param kwargs:字典参数
        """
        self.dirty_notify_fun_ls.append([fun, args, kwargs])
    
    def add_client_flag(self, k, notify=True):
        """
        增加客户端脏数据标志
        :param k:脏数据标志
        """
        self.client_dirty_flag.add_flag(k)
        if notify:
            self.__notify_client_dirty()
        
    def add_client_flag_ls(self, k_ls, notify=True):
        """
        增加客户端脏数据标志
        :param k_ls:脏数据标志列表
        """
        self.client_dirty_flag.add_flag_set(set(k_ls))
        if notify:
            self.__notify_client_dirty()
        
    def add_db_flag(self,k, notify=True):
        """
        增加db脏数据标志
        :param k:脏数据标志
        """
        self.db_dirty_flag.add_flag(k)
        if notify:
            self.__notify_client_dirty()

    def add_db_flag_ls(self,k_ls,notify=True):
        """
        增加db脏数据标志
        :param k_ls:脏数据标志列表
        """
        self.db_dirty_flag.add_flag_set(set(k_ls))
        if notify:
            self.__notify_client_dirty()
        
    def add_flag(self, k):
        """
        增加db/client脏数据标志
        :param k:脏数据标志
        """
        self.add_client_flag(k,False)
        self.add_db_flag(k,False)
        self.__notify_client_dirty()
    
    def add_flag_ls(self, k_ls):
        """
        增加db/client脏数据标志
        :param k_ls:脏数据标志列表
        """
        self.add_client_flag_ls(k_ls,False)
        self.add_db_flag_ls(k_ls,False)
        self.__notify_client_dirty()
        
    def reset_client_flags(self, reset_value):
        """
        重置客户端脏数据标志位
        :param reset_value:重置的值
        """
        self.client_dirty_flag.reset_flags(reset_value)
    
    def get_client_dirty_attr(self):
        """
        获取脏的角色属性
        """
        attr_dict = {}
        
        # 获取脏属性字典
        dirty_key_set = self.client_dirty_flag.get_dirty_keys()
        if dirty_key_set and self.keep_client_keys:
            dirty_key_set.update(set(self.keep_client_keys))
        for k in dirty_key_set:
            attr_dict[k] = self.__get_class_attr(k)                
        
        # 清除脏数据标志
        if attr_dict:
            self.client_dirty_flag.reset_flags(False)
            
        return attr_dict
    
    def get_client_attrs(self):
        """
        获取所有的客户端属性，不分脏与否
        """
        attr_dict = {}
        
        all_keys = self.client_dirty_flag.get_all_keys()       
        for k in all_keys:
            attr_dict[k] = self.__get_class_attr(k)
            
        return attr_dict 
        
    def get_db_dirty_attr(self):
        """
        获取脏的db属性
        """
        attr_dict = {}
        
        # 获取db脏属性
        dirty_keys_set=self.db_dirty_flag.get_dirty_keys()
        if dirty_keys_set and self.keep_client_keys:
            dirty_keys_set.update(set(self.keep_client_keys))
        for k in dirty_keys_set:
            attr_dict[k] = self.__get_class_attr(k)
        
        if attr_dict:
            self.db_dirty_flag.reset_flags(False)
        return attr_dict


# 操作标志
UPD_CLIENT_OPER="upd"   # client update
DEL_CLIENT_OPER="del"   # client delete

DB_OPER_ORDER = [
    DB_OPER_TYPE_INSERT,
    DB_OPER_TYPE_UPDATE,
    DB_OPER_TYPE_DELETE
] = [
    'insert',
    'update',
    'delete'
]
    
# 数据类型
DB_DATA = 0      # 数据类型， db
CLIENT_DATA = 1   # 数据类型， client
class DirtyDictProcess(object):
    """
    逻辑脏字典处理类
    可以处理多行数据
    可以处理多人数据
    可以处理增加/删除/修改记录
    """
    def __init__(self, key_ls=None):
        """
        类初始方法
        :param logic_flag:逻辑标志
        :param table_name:表名
        :param key_ls: 主键key字段列表
        """
        self.key_ls = key_ls if key_ls else []
          
        # 客户端脏数据字典,格式 {'key':{0:{k:{v},,}, 1:[{v},,]},,,,}
        self.client_dirty_dic = {}
        
        # DB脏数据字典,格式 {'key':{0:{k:{v},,}, 1:[{v}],2:{k:{v},,}},,,,}
        self.db_dirty_dic = {}
    
    def __mk_key_dict(self, vdict):
        try:
            dic = dict((key,vdict[key]) for key in self.key_ls)
        except:
            logging.warn('DirtyDictProcess::__mk_key_dict key not enough!,need key_ls:%s, dict:%s'%(self.key_ls,vdict))
            raise
        return dic
    
    def __get_data_dic(self,data_type):
        if data_type == DB_DATA:
            return self.db_dirty_dic
        elif data_type == CLIENT_DATA:
            return self.client_dirty_dic
        else:
            return None
    
    def __dirty_oper(self, data_type, oper_type, key, vdict):
        data_dic = self.__get_data_dic(data_type)
        role_dirty_dict = data_dic.setdefault(key, {})
        
        # delete 采用list存储
        if oper_type == DB_OPER_TYPE_DELETE or oper_type == DEL_CLIENT_OPER:
            ls = role_dirty_dict.setdefault(oper_type, [])
            kdict = self.__mk_key_dict(vdict)
            ls.append(kdict)
            
        # update/insert 采用字典方式存储
        else:
            dic = role_dirty_dict.setdefault(oper_type, {})
            v = dic.setdefault(key, {})
            v.update(vdict)
    
    """
    # 客户端操作
    """
    def ist_client_dict(self, key, vdict):
        """
    insert客户端脏字典
        :param key:主键id
        :param vdict:脏数据字典,必须带上所有的key
        """
        if not vdict:
            return
        self.__dirty_oper(CLIENT_DATA, UPD_CLIENT_OPER, key, vdict)
        
    def upd_client_dict(self, key, vdict):
        """
    update客户端脏字典
        :param key:主键id
        :param vdict:脏数据字典,必须带上所有的key
        """
        if not vdict:
            return
        self.__dirty_oper(CLIENT_DATA, UPD_CLIENT_OPER, key, vdict)
            
    def del_client_dict(self, key, vdict):
        """
    delete客户端脏字典
        :param key:主键id
        :param vdict:脏数据字典,必须带上所有的key
        """
        if not vdict:
            return
        self.__dirty_oper(CLIENT_DATA, DEL_CLIENT_OPER, key, vdict)
        
    def get_client_dirty_dict(self, key):
        """
        获取脏的主键字典数据
        :param key:主键id
        """
        # 拷贝一份脏数据
        dirty_dic = self.client_dirty_dic.setdefault(key, {})
        
        # 省去upd的key
        upd_dic = dirty_dic.get(UPD_CLIENT_OPER,{}).values()
        if upd_dic:
            dirty_dic[UPD_CLIENT_OPER]=upd_dic
        
        # 赋予新的空字典
        self.client_dirty_dic[key] = {}
        
        # 加上logic 标志        
        return dirty_dic

    """
    # db操作
    """
    def ist_db_dict(self, key, vdict):
        """
    insert db脏字典
        :param key:主键id
        :param vdict:脏数据字典,必须带上所有的key
        """
        if not vdict:
            return
        self.__dirty_oper(DB_DATA, DB_OPER_TYPE_INSERT, key, vdict)
                  
    def upd_db_dict(self, key, vdict):
        """
    update db脏字典
        :param key:主键id
        :param vdict:脏数据字典,必须带上所有的key
        """
        if not vdict:
            return
        need_upd = True
        
        # 如果该key在del里面，不更新
        role_dirty_dict = self.db_dirty_dic.get(key, {})
        del_dic = role_dirty_dict.get(DB_OPER_TYPE_DELETE,{})
        if key in del_dic:
            return
        
        # 更新ist里面的key
        role_dirty_dict = self.db_dirty_dic.get(key, {})
        ist_dic = role_dirty_dict.get(DB_OPER_TYPE_INSERT,{})
        if key in ist_dic:
            need_upd= False # 直接更新ist里面的字典，不需要单独update
            ist_dic[key].update(vdict)
        
        if need_upd:
            self.__dirty_oper(DB_DATA, DB_OPER_TYPE_UPDATE, key, vdict)
        
    def del_db_dict(self, key, vdict):
        """
    delete db脏字典
        :param key:主键id
        :param vdict:脏数据字典,必须带上所有的key
        """
        if not vdict:
            return
        need_del=True
        
        # 删除upd里面的key
        role_dirty_dict = self.db_dirty_dic.get(key, {})
        upd_dic = role_dirty_dict.get(DB_OPER_TYPE_UPDATE,{})
        if key in upd_dic:
            upd_dic.pop(key)
            if not upd_dic:
                role_dirty_dict.pop(DB_OPER_TYPE_UPDATE)
        
        # 删除ist里面的key
        role_dirty_dict = self.db_dirty_dic.get(key, {})
        ist_dic = role_dirty_dict.get(DB_OPER_TYPE_INSERT,{})
        
        if key in ist_dic:
            ist_dic.pop(key)
            if not ist_dic:
                role_dirty_dict.pop(DB_OPER_TYPE_INSERT)
            need_del =False # 如果删除的字典还在ist的缓存里面，不需要记录删除
        
        if need_del:
            self.__dirty_oper(DB_DATA, DB_OPER_TYPE_DELETE, key, vdict)

    def get_db_dirty_dict(self, key):
        """
        获取主键脏的db数据
        :param key:主键id
        """
        db_dirty_dic = self.db_dirty_dic.setdefault(key, {})
        
        # 省去upd的key
        upd_dic = db_dirty_dic.get(DB_OPER_TYPE_UPDATE,{}).values()
        if upd_dic:
            db_dirty_dic[DB_OPER_TYPE_UPDATE]=upd_dic
        
        # 省去ist的key
        ist_dic = db_dirty_dic.get(DB_OPER_TYPE_INSERT,{}).values()
        if ist_dic:
            db_dirty_dic[DB_OPER_TYPE_INSERT]=ist_dic
        
        # 赋予新的空字典
        self.db_dirty_dic[key]={}
        
        return db_dirty_dic
    
    def get_db_dirty_dicts(self):
        """
        获取所有主键的脏的db数据
        """
        db_dirty_dicts={}
        dirty_key_ls = self.db_dirty_dic.keys()
        for key in dirty_key_ls:
            db_dirty = self.get_db_dirty_dict(key)
            
            # 数据整合一起
            for dirty_flag,dirty_data_ls in db_dirty.iteritems():
                dirty_flag_ls = db_dirty_dicts.setdefault(dirty_flag,[])
                dirty_flag_ls.extend(dirty_data_ls)
                
        # 赋予新的空字典
        self.db_dirty_dic={}
                
        return db_dirty_dicts

    """
    # db/client同时操作
    """
    def ist_dict(self,key, vdict):
        """
    insert client/db脏字典
        :param key:主键id
        :param vdict:脏数据字典,必须带上所有的key
        """
        self.ist_client_dict(key, vdict)
        self.ist_db_dict(key, vdict)
                  
    def upd_dict(self,key, vdict):
        """
    update client/db脏字典
        :param key:主键id
        :param vdict:脏数据字典,必须带上所有的key
        """
        self.upd_client_dict(key, vdict)
        self.upd_db_dict(key, vdict)
        
    def del_dict(self,key,vdict):
        """
    delete client/db脏字典
        :param key:主键id
        :param vdict:脏数据字典,必须带上所有的key
        """
        self.del_client_dict(key, vdict)
        self.del_db_dict(key, vdict)