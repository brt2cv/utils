#!/usr/bin/env python

###############################################################################
# Name:         exec_uic
# Purpose:
# Author:       Bright Li
# Modified by:
# Created:      2019-10-08
# Version:      [0.1.2]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

import os.path
from PyQt5.uic import compileUi, compileUiDir

def compile_file(path, force_rebuild=True, suffix=""):
    if not os.path.exists(path):
        # print(f"文件【{path}】不存在")
        raise FileNotFoundError(f"文件【{path}】不存在")

    file_name, _ = os.path.splitext(path)
    compiler_creation = file_name + suffix + ".py"

    if not force_rebuild and os.path.exists(compiler_creation):
        print("[-] 已存在ui编译文件【{}】，跳过该文件编译".format(path))
        return

    with open(compiler_creation, "w", encoding="utf8") as fp:
        compileUi(path, fp)
        print("[+] 完成ui文件编译【{}】".format(path))

def compile_dir(path, recurse=True):
    if not os.path.exists(path):
        raise FileNotFoundError

    try:
        compileUiDir(path, recurse)
        print("[+] 完成目录【{}】的 *.ui 文件编译".format(path))  # 在cmder中运行正常
    # except UnicodeDecodeError:
    #     # compileUiDir使用系统编码格式，Windows环境gbk可能导致错误
    #     for root, dirs, files in os.walk(path):
    #         for file_path in files:
    #             _, ext = os.path.splitext(file_path)
    #             if ext != ".ui":
    #                 continue
    #             compile_file(os.path.join(root, file_path))
    #     print("[+] 完成目录【{}】的 *.ui 文件编译".format(path))
    except Exception as e:
        print(f"Error -->> {e}")


if __name__ == "__main__":
    import sys

    for index, file in enumerate(sys.argv):
        if index == 0:  continue
        if not os.path.exists(file):
            print(f'No such file: 【{file}】')
            continue
        if os.path.isdir(file):
            compile_dir(file)
        else:
            compile_file(file)
