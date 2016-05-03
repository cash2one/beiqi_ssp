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
from lib.common import *
from services_control import *
from utils.openfire.user_service import UserService

def find_unittest_modules(path, excluded_dirs=None,excluded_files=None):
    """
    遍历unittest模块：以ztest开头的文件目录，输出所有py模块
    """
    if not excluded_dirs:
        excluded_dirs = ['.idea']
    if not excluded_files:
        excluded_files = ['__init__.py','main.py']

    ztest_dir_set = set([])
    ztest_module_set = set([])
    for parent, dir_names, filenames in os.walk(path):
        for dir_name in dir_names:
            if dir_name in excluded_dirs:
                continue
            dir_path = os.path.join(parent,dir_name)
            dir_set,module_set=find_unittest_modules(dir_path)
            ztest_dir_set.union(dir_set)
            ztest_module_set.union(module_set)

        if platform.system() == "Linux":
            parent_name = parent.split('/')[-1]
        else:
            parent_name = parent.split('\\')[-1]

        if not parent_name.startswith("utest_"):
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
    UserService(OPENFIRE_IP, OPENFIRE_PORT)

    # 如果sm在本地，重启所有的服务
    if ParamCacher().is_sm_local:
        restart_services()

    time.sleep(SYNC_WAIT_TIME)

    main_parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    unittest_dirs, unittest_modules = find_unittest_modules(main_parent_dir)

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
