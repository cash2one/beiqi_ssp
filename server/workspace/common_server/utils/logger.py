# coding=utf-8
"""
Created on 2015-4-22

@author: Jay
"""
from logging.handlers import TimedRotatingFileHandler
import logging
import sys
import os
import platform

DefaultLinuxLogDir = '/var/log/home_internet'
DefaultWindowsLogDir = 'C:\\home_internet'


def get_log_path(server_name=None):
    sys_platform = platform.system()
    if sys_platform == 'Linux':
        log_path = DefaultLinuxLogDir
    else:
        log_path = DefaultWindowsLogDir
    if server_name:
        log_path = os.path.join(log_path, server_name)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    return log_path


def mk_log_file(dir_name, file_name=None):
    # Get Dir
    if dir_name is None:
        if platform.system() == 'Linux':
            dir_name = DefaultLinuxLogDir
        else:
            dir_name = DefaultWindowsLogDir
    
    # check direction
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
    # Get File
    if platform.system() == 'Linux':
        file_name = dir_name + '/' + file_name
    else:
        file_name = dir_name + '\\' + file_name

    return dir_name, file_name


def auth(dirname, filename):
    # Set Auth
    if platform.system() == 'Linux':
        os.chmod(filename, 0777)


back_up_out = sys.stdout
back_up_err = sys.stderr

# sys.stdout = None
# sys.stderr = None


class NullOut:
    """
    什么都不干的流处理
    """

    def __init__(self):
        pass

    def flush(cls):
        pass

    def write(self, *arsg):
        pass

    def writelines(self, *args):
        pass

    def __str__(self):
        return 'Null_Out'

    @staticmethod
    def fileno():
        return - 1

    flush = classmethod(flush)
    write = classmethod(write)
    writelines = classmethod(writelines)
    __str__ = classmethod(__str__)
    fileno = classmethod(fileno)


def stream_state():
    """
    显示当前流的输出状态
    """
    info("stdout = %s" % sys.stdout)
    info("stderr = %s" % sys.stderr)


def enable_print():
    """
    开启项目中 使用print 调用的输出
    """
    sys.stdout = back_up_out
    # sys.stderr = back_up_err
    stream_state()


def disable_print():
    """
    关闭标准输出 重定向到 什么都不干的流
    使用print 调用的输出
    """
    sys.stdout = NullOut
    stream_state()

_logger = None
AFTER_DEBUG_LOG_OPER = None
AFTER_INFO_LOG_OPER = None
AFTER_WARN_LOG_OPER = None
AFTER_ERROR_LOG_OPER = None
AFTER_FATAL_LOG_OPER = None
AFTER_OPER_TAG = None


def getlogger():
    """
    获得Logger 如果没初始化 先初始化
    """
    assert _logger is not None, "please init logger!"
    return _logger


def init_log(server_name, tag):
    """
    #初始化LOGGEr 设置简单输出模式 流用文件和 标准输出  等级现在设为
    """
    global _logger
    if _logger:
        return _logger
    
    logfile_dir, _ = mk_log_file(get_log_path(server_name), tag)
    
    d_fommater = formatter_dct.get('simple')
    
    logger = logging.getLogger('INFO')
    fatal_logger = logging.getLogger('FATAL')
     
    fatal_log_handler = get_fatal_log_handler(logfile_dir, tag)
    fatal_logger.addHandler(fatal_log_handler)
    fatal_logger.setLevel(logging.CRITICAL)
     
    f_handler = get_day_log_handler(logfile_dir, tag)
    logger.addHandler(f_handler)
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler(back_up_out)
    stream_handler.setFormatter(d_fommater)
      
    logging.root.addHandler(stream_handler)
    
    _logger = logger
    return _logger


def get_day_log_handler(logfile_dir, tag):
    if not os.path.isdir(logfile_dir):
        os.makedirs(logfile_dir)      
    
    handler = TimedRotatingFileHandler(os.path.join(logfile_dir, "%s.log" % tag), when="midnight")
    handler.setFormatter(formatter_dct.get('simple'))
    handler.setLevel(logging.INFO)
    return handler


def get_fatal_log_handler(logfile_dir, tag):
    if not os.path.isdir(logfile_dir):
        os.makedirs(logfile_dir)      
    
    handler = TimedRotatingFileHandler(os.path.join(logfile_dir, "%s_fatal.log" % tag), when="midnight")
    handler.setFormatter(formatter_dct.get('all'))
    handler.setLevel(logging.FATAL)
    return handler

# 不同的格式化输出 信息详尽不一样
formatter_dct = {'simple': logging.Formatter("[%(levelname)s] [P%(process)d] T%(thread)d] %(asctime)s] %(message)s ",
                                             "%Y-%m-%d %H:%M:%S"),
                 'normal': logging.Formatter("[%(levelname)s] %(asctime)s] %(module)s.%(funcName)s]  %(message)s ",
                                             "%Y-%m-%d %H:%M:%S"),
                 'detail': logging.Formatter("[%(levelname)s] %(asctime)s] %(filename)s(%(lineno)d)]  %(message)s ",
                                             "%Y-%m-%d %H:%M:%S"),
                 'all':    logging.Formatter("[%(levelname)s] %(asctime)s] %(filename)s(%(lineno)d)"
                                             " %(module)s.%(funcName)s P%(process)d T%(thread)d]  %(message)s",
                                             "%Y-%m-%d %H:%M:%S"),
                 }


def set_formatter(formmater_name):
    """
    设置LOG 输出格式 不同的格式 详尽信息不一样 目前有 simple normal detail all四种  默认simple egg. set_formatter normal
    """
    formater = formatter_dct.get(formmater_name)
    logger = getlogger()
    if formater:
        for handle in logger.handlers:
            handle.setFormatter(formater)
    return


def set_notset():
    """
    将调试等级设置成NOTSET等级 使用log等级低于NOTSET等级的log将会被屏蔽FATAL > ERROR > WARN > INFO > DEBUG > NOTSET
    """
    getlogger().setLevel(logging.NOTSET)


def set_debug():
    """
    将调试等级设置成DEBUG等级 使用log等级低于DEBUG等级的log将会被屏蔽FATAL > ERROR > WARN > INFO > DEBUG > NOTSET
    """
    getlogger().setLevel(logging.DEBUG)


def set_info():
    """
    将调试等级设置成INFO等级 使用log等级低于INFO等级的log将会被屏蔽FATAL > ERROR > WARN > INFO > DEBUG > NOTSET
    """
    getlogger().setLevel(logging.INFO)


def set_warn():
    """
    将调试等级设置成WARN等级 使用log等级低于WARN等级的log将会被屏蔽FATAL > ERROR > WARN > INFO > DEBUG > NOTSET
    """
    getlogger().setLevel(logging.WARN)


def set_error():
    """
    将调试等级设置成ERROR等级 使用log等级低于ERROR等级的log将会被屏蔽FATAL > ERROR > WARN > INFO > DEBUG > NOTSET
    """
    getlogger().setLevel(logging.ERROR)


def set_fatal():
    """
    将调试等级设置成FATAL等级 使用log等级低于FATAL等级的log将会被屏蔽 FATAL > ERROR > WARN > INFO > DEBUG > NOTSET
    """
    getlogger().setLevel(logging.FATAL)

LOGGER_LEVELS = [FATAL, ERROR, WARNING, INFO, DEBUG] = ["fatal", "error", "warning", "info", "debug"]
def set_logger_level(str_logger_level):
    str_logger_level = str_logger_level.lower()
    assert str_logger_level in LOGGER_LEVELS
    if str_logger_level == FATAL:
        set_fatal()
    elif str_logger_level == ERROR:
        set_error()
    elif str_logger_level == WARNING:
        set_warn()
    elif str_logger_level == INFO:
        set_info()
    elif str_logger_level == DEBUG:
        set_debug()


def logger_help(*args):
    """
    logger 的使用帮助
    """
    info(__doc__)


def debug(msg, *args, **kwargs):
    getlogger().debug(msg, *args, **kwargs)                        # 服务器出现严重错误用这个
    if AFTER_DEBUG_LOG_OPER:
        AFTER_DEBUG_LOG_OPER("%s\n%s" % (AFTER_OPER_TAG, msg), *args)


def info(msg, *args, **kwargs):
    getlogger().info(msg, *args, **kwargs)                        # 服务器出现严重错误用这个
    if AFTER_INFO_LOG_OPER:
        AFTER_INFO_LOG_OPER("%s\n%s" % (AFTER_OPER_TAG, msg), *args)


def warn(msg, *args, **kwargs):
    getlogger().warn(msg, *args, **kwargs)                        # 服务器出现严重错误用这个
    if AFTER_WARN_LOG_OPER:
        AFTER_WARN_LOG_OPER("%s\n%s" % (AFTER_OPER_TAG, msg), *args)


def error(msg, *args, **kwargs):
    getlogger().error(msg, *args, **kwargs)                        # 服务器出现严重错误用这个
    if AFTER_ERROR_LOG_OPER:
        AFTER_ERROR_LOG_OPER("%s\n%s" % (AFTER_OPER_TAG, msg), *args)


def fatal(msg, *args, **kwargs):
    logging.getLogger('FATAL').fatal(msg, *args, **kwargs)                     # 服务器出现致命错误用这个
    if AFTER_FATAL_LOG_OPER:
        try:
            AFTER_FATAL_LOG_OPER("%s\n%s" % (AFTER_OPER_TAG, msg), *args)
        except Exception, e:
            pass
