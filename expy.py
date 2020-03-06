
###############################################################################
# Name:         expy
# Usage:        expand_venv("$HOME/enpy/qt5")
#               path_append("./venv/Lib/site-packages", __file__)
# Author:       Bright Li
# Modified by:
# Created:      2020-03-06
# Version:      [2.1.1]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

import sys
import os

def path_expand(dir_lib, __file__=None, addsitedir=False):
    """ 当__file__为None时，dir_lib为绝对路径（或相对工作目录）
        否则，相对于传入的__file__所在目录引用dir_lib
    """
    if __file__ is not None:
        dir_lib = os.path.join(os.path.dirname(__file__), dir_lib)
    dir_lib_abs = os.path.abspath(dir_lib)
    if os.path.exists(dir_lib_abs):
        if dir_lib_abs not in sys.path:
            if addsitedir:
                import site
                str_func = "site_expand: "
                site.addsitedir(dir_lib_abs)
            else:
                str_func = "path_expand: "
                sys.path.append(dir_lib_abs)
            print(str_func + f"动态加载Lib目录【{dir_lib_abs}】")
    else:
        raise Exception(f"无效的路径【{dir_lib_abs}】")
        # print(f"path_append: 无效的路径【{dir_lib_abs}】")

def site_expand(dir_lib, __file__=None):
    """ 功能上强于path_append，会调用path目录下的*.pth文件
        但pyinstaller打包时，会提示site无法导入addsitedir问题
    """
    path_expand(dir_lib, __file__, True)

#####################################################################
from platform import system, python_version_tuple
platform_is_Windows = system() == "Windows"
python_version = ".".join(python_version_tuple()[:2])

def venv_expand(path_venv):
    LIB_RPATH_PKG = "lib/site-packages" if platform_is_Windows else \
                    "lib/python{}/site-packages".format(python_version)
    dir_lib = os.path.join(path_venv, LIB_RPATH_PKG)
    # if not os.path.exists(dir_lib):
    #     raise Exception(f"无效的路径【{dir_lib}】")
    site_expand(dir_lib)

def topdir(dir_dst, override=False):
    dir_dst_abs = os.path.abspath(dir_dst)
    # 修改顶层目录
    if override:
        sys.path[0] = dir_dst_abs  # os.getcwd()
    else:
        sys.path.insert(0, dir_dst_abs)
    return dir_dst_abs

chdir = os.chdir

def _expy(folder_name):
    """ 注意，目前的配置目录仅自用（个人配置的所有venv目录均位于 '$HOME/enpy' ）"""
    ENPY_PREFIX = os.path.join(os.getenv("HOME"), "enpy")
    path_venv = os.path.join(ENPY_PREFIX, folder_name)
    venv_expand(path_venv)

def expy_pydev():
    path_pydev = os.path.join(os.getenv("HOME"), "local/utils/pydev")
    site_expand(path_pydev)
