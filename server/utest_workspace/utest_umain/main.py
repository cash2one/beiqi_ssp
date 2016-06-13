#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-22

@author: Jay
"""
import site
import os
import traceback
cur_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
site.addsitedir(cur_path)
from utest_lib.common import *
from services_control import *


def find_unittest_modules(path, excluded_dirs=None, excluded_files=None):
    """
    遍历unittest模块：以ztest开头的文件目录，输出所有py模块
    """
    excluded_dirs = excluded_dirs if excluded_dirs else []
    excluded_dirs.extend(['.idea'])

    excluded_files = excluded_files if excluded_files else []
    excluded_files.extend(['__init__.py','main.py'])

    ztest_dir_set = set([])
    ztest_module_set = set([])
    for parent, dir_names, filenames in os.walk(path):
        exc_dirs = [exc_dir for exc_dir in excluded_dirs if exc_dir in parent]
        parent_name = os.path.basename(parent)
        if exc_dirs or not parent_name.startswith("utest_"):
            continue

        for file_name in filenames:
            if not file_name.endswith(".py") or file_name in excluded_files:
                continue
            ztest_module_set.add(file_name.split(".")[0])
            ztest_dir_set.add(parent)
    return ztest_dir_set, ztest_module_set


if __name__ == '__main__':
    logger.init_log("utest", "utest")
    logger.warn("utest_umain start args: %s" % sys.argv)

    # 暂时不处理服务的开启关闭
    # # 如果sm在本地，重启所有的服务
    # if ParamCacher().is_sm_local:
    #     restart_services()

    time.sleep(SYNC_WAIT_TIME)

    main_parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    unittest_dirs, unittest_modules = find_unittest_modules(main_parent_dir, excluded_dirs)
    print "unittest_dirs,", unittest_dirs
    print "unittest_modules,", unittest_modules

    # add module path
    [sys.path.append(path_dir) for path_dir in unittest_dirs]

    # import module
    try:
        for module in unittest_modules:
            exec("from %s import *" % module)
    except:
        print traceback.format_exc()
        if ParamCacher().is_sm_local:
            stop_services()
        sys.exit(1)

    time.sleep(SYNC_WAIT_TIME)

    # run tests
    tmain = unittest.main(exit=False, argv=sys.argv[:1])

    if ParamCacher().is_sm_local:
        stop_services()
    print "unittest finish!!!"
    sys.exit(not tmain.result.wasSuccessful())
