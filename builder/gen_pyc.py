#!/usr/bin/env python

###############################################################################
# Name:         gen_pyc
# Purpose:
# Author:       Bright Li
# Modified by:
# Created:      2019-10-09
# Version:      [0.2.0]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

import shutil
import os.path
from os import makedirs
import argparse
import re
import compileall

def make_pyc(src_dir, rstr_rx=None, force=True):
    """ 编译特定的目录 """
    rx = re.compile(rstr_rx) if rstr_rx else None
    if not compileall.compile_dir(src_dir,
            force=force,  # 强制刷新之前的编译文件
            rx=rx,  # 需要通过正则表达式忽略的文件，例如 re.compile(r"test.*")
            quiet=1,  # 1: 只显示错误信息; 0: 显示全部信息; 2: 不显示
            legacy=False):  # True: 本地生成同名的 *.pyc 文件
        raise Exception("Something wrong when compile the python-file dir")

def extract_pyc(src_dir, dest_dir):
    # 递归搜集 __pychache__ 目录的 pyc 文件
    # os.walk() 函数如果是后序遍历，则每层结构都是先更新了__pychache__文件
    # 名称后，才处理其父目录；否则则需要重新从顶层遍历目录后执行下述代码
    for root, dirs, files in os.walk(src_dir):
        _, dir_name = os.path.split(root)
        if dir_name == "__pycache__":
            # 替换 *.pyc 文件名称
            for file_name in files:
                # rename the xxx.cpython-34.pyc files
                if re.search(r"\.cpython-[0-9]+\.pyc$", file_name):
                    list_name = file_name.split('.')
                    del list_name[1]
                    os.rename(os.path.join(root, file_name),
                            os.path.join(root, '.'.join(list_name)))

    # 移动 __pycache__ 目录
    if os.path.exists(dest_dir):  # isdir(dest_dir):
        print("目标目录已存在，删除并更新目录")
        shutil.rmtree(dest_dir)

    cache_root = os.path.join(src_dir, "__pycache__")
    if os.path.exists(cache_root):
        shutil.move(cache_root, dest_dir)
    else:
        makedirs(dest_dir)

    for root, dirs, files in os.walk(src_dir):
        if "__pycache__" in dirs:
            relative_path = root.lstrip(src_dir)
            # print(">>", dest_dir, relative_path)
            try:
                src = os.path.join(root, "__pycache__")
                # dst = os.path.join(dest_dir, relative_path)
                dst = dest_dir + relative_path
                shutil.move(src, dst)
            except Exception as e:
                print(f"Error when deal with 【{src}】to【{dst}】")
                print(e)


def getopt():
    parser = argparse.ArgumentParser("gen_pyc.py", description="Python Compiling Generator【v0.0.1】2018/09/01")
    parser.add_argument("path_src", action="store", help="the source dir to compile")
    parser.add_argument("-e", "--extract", action="store", help="extract the pyc from __pychche__ recursively, and point the build_dir")
    parser.add_argument("-f", "--force", action="store_true", help="update the pyc forcely")
    return parser.parse_args()

if __name__ == "__main__":
    # ignore_dirs = ["runtime/", "test/", "tmp/"]
    ignore_dirs = r"(runtime|test|tmp)"  # r"(runtime|test|tmp)$"

    args = getopt()
    force = True if args.force else False
    # build the pyc
    make_pyc(args.path_src, ignore_dirs, force)

    # extract __pycache__
    if args.extract:
        extract_pyc(args.path_src, args.extract)
