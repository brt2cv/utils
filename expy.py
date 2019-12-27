
###############################################################################
# Name:         expy
# Usage:        expand_venv("$HOME/enpy/qt5")
#               path_append("./venv/Lib/site-packages", __file__)
# Author:       Bright Li
# Modified by:
# Created:      2019-12-11
# Version:      [2.0.0]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

import sys
import os

def path_expand(dir_lib, __file__=None):
    """ 当__file__为None时，dir_lib为绝对路径（或相对工作目录）
        否则，相对于传入的__file__所在目录引用dir_lib
    """
    if __file__ is not None:
        dir_lib = os.path.join(os.path.dirname(__file__), dir_lib)
    if os.path.exists(dir_lib):
        if dir_lib not in sys.path:
            print(f"path_append: 动态加载Lib目录【{dir_lib}】")
            sys.path.append(dir_lib)
    else:
        # raise Exception(f"无效的路径【{dir_lib}】")
        print(f"path_append: 无效的路径【{dir_lib}】")

def site_expand(dir_lib, __file__=None):
    """ 功能上强于path_append，会调用path目录下的*.pth文件
        但pyinstaller打包时，会提示site无法导入addsitedir问题
    """
    import site

    if __file__ is not None:
        dir_lib = os.path.join(os.path.dirname(__file__), dir_lib)
    if os.path.exists(dir_lib):
        print(f"site_append: 动态加载Lib目录【{dir_lib}】")
        site.addsitedir(dir_lib)
    else:
        raise Exception(f"site_append: 无效的路径【{dir_lib}】")

def venv_expand(path_venv):
    LIB_RPATH_PKG = "lib/site-packages"
    dir_lib = os.path.join(path_venv, LIB_RPATH_PKG)
    # if not os.path.exists(dir_lib):
    #     raise Exception(f"无效的路径【{dir_lib}】")
    site_expand(dir_lib)

def chdir_topdir(dir_dst):
    # 修改工作目录
    os.chdir(dir_dst)
    cwd = os.getcwd()
    # 修改顶层目录
    sys.path[0] = cwd

# def _expy(folder_name):
#     """ 注意，目前的配置目录仅自用（个人配置的所有venv目录均位于 '$HOME/enpy' ）"""
#     ENPY_PREFIX = os.path.join(os.getenv("HOME"), "enpy")
#     path_venv = os.path.join(ENPY_PREFIX, folder_name)
#     venv_expand(path_venv)
