###############################################################################
# Name:         debug
# Usage:
# Author:       Bright Li
# Modified by:
# Created:      2019/12/11
# Version:      [0.1.0]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

import sys
import traceback

def get_frame():
    func_name = sys._getframe(1).f_code.co_name
    return func_name

def curr_frame():
    """Return the frame object for the caller's stack frame."""
    try:
        raise Exception
    except:
        return sys.exc_info()[2].tb_frame.f_back

def get_caller_path():
    """ 获取caller调用者模块的路径 """
    path_file = sys._getframe(2).f_code.co_filename  # inspect.stack()[2][1]
    # print("--- sys._getframe: ", path_file)
    # import inspect
    # print("--- inspect.stack: ", inspect.stack()[2][1])
    return path_file

# typedef struct _frame {
#     PyObject_VAR_HEAD
#     struct _frame *f_back;    /* 调用者的帧 */
#     PyCodeObject *f_code;     /* 帧对应的字节码对象 */
#     PyObject *f_builtins;     /* 内置名字空间 */
#     PyObject *f_globals;      /* 全局名字空间 */
#     PyObject *f_locals;       /* 本地名字空间 */
#     PyObject **f_valuestack;  /* 运行时栈底 */
#     PyObject **f_stacktop;    /* 运行时栈顶 */
#     ……
# }

def dump_exception(e):
    print("%s EXCEPTION:" % e.__class__.__name__, e)
    traceback.print_tb(e.__traceback__)

# decorator
def find_caller(func):
    def wrapper(*args,**kwargs):
        import sys
        f=sys._getframe()
        filename=f.f_back.f_code.co_filename
        lineno=f.f_back.f_lineno
        print('######################################')
        print('caller filename is ',filename)
        print('caller lineno is',lineno)
        print('the passed args is',args,kwargs)
        print('######################################')
        func(*args,**kwargs)
    return wrapper

# decorator
def elapsed(func):
    from time import time
    def running(*args, **kwarg):
        time_0 = time()
        # str_0 = f"起始时刻：{ctime()}"
        res = func(*args, **kwarg)
        time_1 = time()
        # str_1 = f"结束时刻：{ctime()}"

        consuming = time_1 - time_0
        print(f"耗时统计：{consuming}")  # {str_0}, {str_1},

        return res
    return running
