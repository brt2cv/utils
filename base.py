###############################################################################
# Name:         base(基础功能集成)
# Usage:
# Author:       Bright Li
# Modified by:
# Created:      2020-03-06
# Version:      [0.1.3]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

import os.path
import sys
from .debug import get_caller_path

# from .log import getLogger
# logger = getLogger()

isPy3 = sys.version_info.major >= 3
# isPy36 = sys.version_info[:2] >= (3, 6)

from platform import system
isWindows = system() == "Windows"

if isPy3:
    if sys.version_info[:2] >= (3, 6):
        from pathlib import Path
        def isPath(f):
            return isinstance(f, (bytes, str, Path))
    else:
        def isPath(f):
            return isinstance(f, (bytes, str))

def isDir(f):
    return isPath(f) and os.path.isdir(f)

def rpath2curr(f):
    """ 这个命名可能并不恰当，表示相对__file__的文件，转为绝对路径 """
    path_caller = get_caller_path()
    # print("---- path_caller: ", path_caller)
    # return os.path.relpath(f, path_caller)
    path_dir = os.path.dirname(path_caller)
    path_abs = os.path.join(path_dir, f)
    # print("__", path_abs)
    return path_abs

def rpath2abs(path_rel, start=None):
    """ if start is None, equals to param: __file__ """
    path_caller = get_caller_path() if start is None else start
    # return os.path.relpath(path_rel, path_caller)
    path_dir = os.path.dirname(path_caller)
    return os.path.join(path_dir, path_rel)

#####################################################################

_instance = {}  # 略显丑陋，进程不安全（Python多进程不共享全局变量）
def singleton(cls):
    # 对于单例类，无法通过继承的方式节省代码
    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner

#####################################################################

class Deletable:
    def __init__(self):
        super().__init__()
        self.isDel = False

    def __del__(self):
        # logger.debug("__del__")
        if not self.isDel:
            self.destroy()

    def destroy(self):
        self.isDel = True

#####################################################################
import importlib
import inspect

def module_func(module):
    """ return a dict of {name: method_obj} """
    list_ = inspect.getmembers(module, inspect.isfunction)
    return dict(list_)

def module_class(module):
    """ return a dict of {name: class_obj} """
    list_ = inspect.getmembers(module, inspect.isclass)
    return dict(list_)

def module_name(module):
    return module.__name__

def module_path(module):
    return module.__file__

def reload_package(dir_package):
    import glob
    modules = glob.glob(os.path.join(dir_package, "*.py"))
    list_modules = [ f for f in modules
                     if os.path.isfile(f) and not f.endswith('__init__.py')]

    for path_module in list_modules:
        module = path2module(path_module)
        importlib.reload(module)

def path2strmod(path):
    if os.path.isabs(path):
        raise Exception("请使用相对路径载入项目模块")

    without_ext, _ = os.path.splitext(path)
    # path_linux = without_ext.replace("\\", "/")
    path_linux = without_ext.replace("\\", ".")
    module = path_linux.replace("/", ".")
    return module

def path2module(path, package=None):
    str_module = path2strmod(path)
    return importlib.import_module(str_module, package)

"""
def path2module2(path):
    name = os.path.basename(path).splitext()[0]
    module_spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module
"""

class IPluginObject:
    def run(self, *args, **kwargs):
        pass

def import_plugin(module, package=None, **kwargs):
    """ module:
          - 'top/package/module.py'
          - "top.package.module"
        kwargs:
          - "package": None
    """
    if isinstance(module, str):
        if module.find("/") >= 0 or module.rfind(".py") >= 0:
            module = path2strmod(module)
        module = importlib.import_module(module, package)

    plugin_obj = module.export_plugin(**kwargs)
    return plugin_obj

# def export_plugin():
#     """ return a Plugin-Class Object """
#     return plugin_obj

#####################################################################
import threading

def synchronized(func):
    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func
