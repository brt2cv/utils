#!/usr/bin/env python3
# @Date    : 2020-10-06
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.2.2


def getopt():
    """
    Usage Example:
        termux-open-url [upload] http://baidu.com
    """
    import argparse

    parser = argparse.ArgumentParser(description="新的工具")
    parser.add_argument("-p", "--path", action="store", help="图像路径")
    return parser.parse_args()


#####################################################################
# getopt@Version : 0.2.2
#####################################################################

from argparse import ArgumentParser

class Cli(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.getopt()

    def getopt(self, dict_args):
        """ dict_args: {
            "-n,--name": {
                "action": "store",
                "type": "string",
                "help": ""
            },
            "x,xpath": "just help string",
            ...
        }
        """
        for name, dict_details in dict_args.items():
            if isinstance(dict_details, str):
                dict_details = {"help": dict_details}

            list_flags = name.split(",")
            if len(list_flags) == 1:
                # 位置参数
                name = list_flags[0]
                self.add_argument(name,
                                  **dict_details)
            else:
                name, flag = list_flags
                if name[0] != "-": name = "-" + name
                if flag[0] != "-": flag = "--" + flag
                self.add_argument(name,
                                  flag,
                                  **dict_details)
                                  # action=dict_details.get("action", "store"),
                                  # type=dict_details.get("type", str),
                                  # help=dict_details.get("help", ""))
        self.args = self.parse_args()

    def input_path_to_list(self, input_string):
        """ 处理输入的文本，如果存在多个路径，返回list """
        path = input_string.strip()
        for q in ["\"", "\'"]:
            multi_files_gap = "{0} {0}".format(q)
            if path.find(multi_files_gap) >= 0:
                list_args = path.split(multi_files_gap)
                # break
                return [path.strip(q) for path in list_args]
        return [path.strip("\"").strip("\'")]

    def parse_path(self, path, callback):
        """ callback is a function, for example, switch_opt(cli, path) """
        import os.path

        if os.path.isdir(path):
            from glob import glob

            print("当前路径为目录，将遍历目录下的所有文件")
            list_files = glob(os.path.join(path, "*"))
            for path in list_files:
                callback(self, path)
        elif os.path.isfile(path):
            callback(self, path)
        else:
            print(f"Error: File [{path}] NOT found.")


if __name__ == "__main__":
    # from utils.cli import Cli

    cli = Cli(description="Resize: 图像缩放与压缩工具")
    cli.getopt({
            "s,size": "缩放至尺寸，如: 800x600",
            "l,limit_size": "递归压缩至受限尺寸，如: 1280x800，可配合'-r'参数使用",
            "r,ratio": "缩放比例（默认: 0.7）",
            "c,compress": {
                "action": "store_true",
                "help":"如果既没有设定ratio，也没有size，则执行压缩操作"},
            "path": "源文件路径",
            # "d,dst": "保存至文件夹",
        })

    # 处理其他参数
    def switch_args(cli, path_file):
        # print(">>>", path_file)
        args = cli.args
        # if args.abc:
        #     pass
        # else:
        #     raise Exception("未知的指令")

    # 处理路径参数（主要用于拖拽文件）
    if cli.args.path:
        cli.parse_path(cli.args.path, switch_args)
    else:
        inputs = input("\n请输入待处理文件path(支持直接拖拽): ")
        while True:
            list_path = cli.input_path_to_list(inputs)
            for path in list_path:
                cli.parse_path(path, switch_args)

            path = input("继续输入path，按[Q]退出: ")
            if path.lower() == "q":
                break

#####################################################################
# end of getopt
#####################################################################
