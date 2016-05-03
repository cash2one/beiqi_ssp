# coding=utf-8
"""
Created on 2015-4-22

@author: Jay
"""
import sys
import os
import types
import traceback

from utils.meta.singleton import Singleton
from utils import comm_func, logger


class Reload(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.model_modify = {}
        
    def init_model_reload_dic(self):
        """
        初始化reload字典
        """
        for name, module in sys.modules.items():
            filename = comm_func.is_code_module(module)
            if not filename:
                continue
            filename = os.path.normpath(filename)
            if not os.path.isfile(filename):
                continue
            
            # 文件上次修改的时间
            disk_time = os.path.getmtime(filename)
            self.model_modify[name] = disk_time
            
    def __str__(self):
        return str(self.model_reload_dic)
    
    def __check_modified(self):
        """
        获得要reload的模块列表
        """
        modules = []    
        for name, module in sys.modules.items():
            filename = comm_func.is_code_module(module)
            if not filename:
                continue
            filename = os.path.normpath(filename)
            if not os.path.isfile(filename):
                continue
    
            # 上次reload的时间
            ls_reload_time = self.model_modify.get(name)
            if not ls_reload_time:  # 找不到第一次reload , 取对应文件上次修改的时间作为上次reload的时间
                modules.append(name)
            else:
                # 文件上次修改的时间
                disk_time = os.path.getmtime(filename)
                if disk_time is not None and ls_reload_time != disk_time:
                    modules.append(name)
        return modules

    def reload(self):
        logger.info("Please Wait.Reloading...")
        modified_list = self.__check_modified()
        module_dict = {}
            
        logger.info('reload modified_list = %s', modified_list)
        for module_name in modified_list:
            module = sys.modules.get(module_name)
            if not module:
                continue
            module_dict[module_name] = module
            
        # 模块以前的内容, 模块修改时间
        save_model_dic, model_modify = {}, {}
        
        has_error, error, file_ls = False, '', []
        for module_name, module in module_dict.items():
            # 潜规则
            # __main__和 以setkup结尾的模块不参与reload
            if module_name == '__main__' or module_name.endswith('setup'): 
                continue
            # 会重读自己 这里 没找到好办法 先try住不处理
            if module: 
                reload_res, save_cotent, error = _reload_module(module)
                filename = comm_func.is_code_module(module)
                file_ls.append(filename)
                save_model_dic[module_name] = [module, save_cotent]
                model_modify[module_name] = os.path.getmtime(filename)
                if reload_res:
                    logger.info('successful reload module %s', module_name)
                else:   
                    has_error = True
                    break
        if has_error:  # 出现reload错误，还原模块
            for _, [module, save_cotent] in save_model_dic.iteritems():
                setattr(module, '__dict__', save_cotent)
            return has_error, error
        else:   # 没有reload错误, 设置reload的模块的修改时间
            self.model_modify.update(model_modify)
            if file_ls:
                return has_error, "\n".join(file_ls)
            else:
                return has_error, "no code file need to reload!"


def _reload_module(module):
    """
    reload module reload模块 (已经加载过的模块 否则的话需要用__import__)
    """
    saved_dict = {}
    saved_dict.update(getattr(module, '__dict__', {}))
    
    sucess, error = True, ''
    try:
        reload(module)
        new_dict = getattr(module, '__dict__', {})
        oldnames = set(saved_dict)
        newnames = set(new_dict)
        for attr_name in newnames & oldnames:
            new_dict[attr_name] = __update(saved_dict[attr_name], new_dict[attr_name])
    except:
        # reload失败,将模块还原
        new_dict.clear()
        new_dict.update(saved_dict)
        
        error, sucess = traceback.format_exc(), False
        logger.fatal('Fail to reload module = %s', module)
        logger.fatal(error)
        
    # 返回reload结果和模块的旧数据方便恢复
    return sucess, saved_dict, error


def __update(oldobj, newobj):
    """
    模块的替换
    @param oldobj:
    @param newobj:
    """
    if oldobj is newobj:
        return newobj
    if hasattr(newobj, "reload_update"):
        return newobj.reload_update(oldobj, newobj)
    if isinstance(newobj, types.ClassType) or isinstance(newobj, types.TypeType):
        return _update_class(oldobj, newobj)
    if isinstance(newobj, types.FunctionType):
        return _update_function(oldobj, newobj)
    if isinstance(newobj, types.MethodType):
        return _update_method(oldobj, newobj)
    if isinstance(newobj, classmethod):
        return _update_classmethod(oldobj, newobj)
    if isinstance(newobj, staticmethod):
        return _update_staticmethod(oldobj, newobj)
    if isinstance(oldobj, types.DictType)\
            or isinstance(newobj, types.DictType):  # 字典类型
        oldobj.update(newobj)
        return oldobj
        
    if isinstance(newobj, types.ListType)\
            or isinstance(newobj, type(set())):
        if oldobj and not newobj:   
            return oldobj
        return newobj
        
    if isinstance(newobj, types.IntType)\
            or isinstance(newobj, types.StringType)\
            or isinstance(newobj, types.BooleanType):  # 三种简单类型
        return newobj
    
    if isinstance(newobj, types.CodeType):  # code类型，如代码中compile编译以后的结果
        return newobj
    
    # 不知道什么类型，放弃检查返回旧的值，reload对于该类型失效。在此处不能返回新的值，防止数据丢失
    return oldobj


def _update_function(oldfunc, newfunc):
    """Update a function object."""
    
    if newfunc.func_closure:    # 有闭包函数，则返回新函数(此处是不得已为之，)
        # ====================潜规则================
        # 有闭包函数的函数不能在其他处被单做指针存储，否则reload会无效
        return newfunc
    oldfunc.__doc__ = newfunc.__doc__
    oldfunc.__dict__.update(newfunc.__dict__)
    oldfunc.__code__ = newfunc.__code__
    oldfunc.__defaults__ = newfunc.__defaults__
    return oldfunc


def _update_method(oldmeth, newmeth):
    """Update a method object."""
    __update(oldmeth.im_func, newmeth.im_func)
    return oldmeth


def _update_class(oldclass, newclass):
    """
    Update a class object.
    """
    if not hasattr(oldclass, '__dict__'):
        return oldclass
    
    olddict = oldclass.__dict__
    newdict = newclass.__dict__
    oldnames = set(olddict)
    newnames = set(newdict)
    for name in newnames - oldnames:
        setattr(oldclass, name, newdict[name])
    for name in oldnames - newnames:
        delattr(oldclass, name)
    for name in oldnames & newnames - {"__dict__", "__doc__", '__init__'}:
        setattr(oldclass, name,  __update(olddict[name], newdict[name]))
    return oldclass


def _update_classmethod(oldcm, newcm):
    """
    Update a classmethod update.
    """
    __update(oldcm.__get__(0), newcm.__get__(0))
    return newcm


def _update_staticmethod(oldsm, newsm):
    """
    Update a staticmethod update.
    """
    __update(oldsm.__get__(0), newsm.__get__(0))
    return newsm
