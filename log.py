
###############################################################################
# Name:         log
# Usage:        from mylib import log
#               logger = log.make_logger(__file__)
#               # logger.setLevel(log.INFO)
# Author:       Bright Li
# Modified by:
# Created:      2019-10-09
# Version:      [0.2.2]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

import inspect
import os.path
import logging
from logging.config import dictConfig

_config = {
    'version': 1,
    'formatters': {
        'default': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
        },
        "myc_brief": {
            'class': 'logging.Formatter',
            'format': '---- [%(levelname)s  %(name)s] ---- %(message)s'
        },
        "myc_detail": {
            'class': 'logging.Formatter',
            'format': '---- [%(levelname)s] %(module)s::%(funcName)s ---- %(message)s'
        },
        "myc_precise": {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(module)s::%(funcName)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'myc_brief',
        },
        'console_detail': {
            'class': 'logging.StreamHandler',
            # 'level': 'INFO',
            'formatter': 'myc_detail',
        },
        'file_template': {
            'class': 'logging.FileHandler',
            'filename': 'mplog.log',
            'mode': 'a',
            'formatter': 'myc_precise',
            "delay": True  # 在输出时再开启Stream流文件
        },
        'errors': {
            'class': 'logging.FileHandler',
            'filename': 'mplog-errors.log',
            'mode': 'w',
            'level': 'ERROR',
            'formatter': 'myc_precise',
            "delay": True
        },
    },
    'loggers': {
        'console': {
            'handlers': ['console_detail'],
            'level': 'DEBUG',
            'propagate': False  # 不向父类传播
        },
        'file': {
            'handlers': ['file_template'],
            'level': 'WARNING',
            'propagate': False
        },
    },
    # 'root': {
    #     'level': 'WARNING',
    #     'handlers': ['console']
    # }
}

dictConfig(_config)

def make_logger(level=None, name=None, output_file=False):  # name='__file__'
    """ 由于每个文件中的logger对象需要独立设定Level，
        不能共用logger；也因此不能使用预定义logger。

        loggers允许共享同一个handler对象。
        但如果是FileHandler，由于handler.stream不同，无法共享handler。
        FileHandler的共享机制，是根据output_file实现的。

        output_file: 
          - strPath: 指定输出路径
          - True: 使用默认log文件 [depressed]
          - Fase: 使用Console输出

        注意：name为None时，会按照当前模块名补充；但如果在同一个模块中
            多次无参调用make_logger，将会得到同一个logger
    """

    if not name:
        # from pprint import pprint
        # pprint(inspect.stack())
        abspath = inspect.stack()[1][1]

        # file_name = os.path.basename(abspath)
        rpath = os.path.relpath(abspath)  # 相对路径
        name, _ = os.path.splitext(rpath)

    isExist = name in logging.Logger.manager.loggerDict
    logger = logging.getLogger(name)

    if not isExist:  # 针对新建的logger
        logger.propagate = False  # 取消父类传播属性

        # logging._handlers 纪录了系统中创建的全部Handler
        # handler = logging._handlers["file" if output_file else "console_detail"]
        if output_file:
            if output_file in logging._handlers:
                # 多个logger写入同一个log文件，则共享handler
                handler = logging._handlers[output_file]
            else:
                # FileHandler使用相同的formatter
                file_formatter = logging._handlers["file_template"].formatter
                handler = logging.FileHandler(output_file, mode='a', delay=True)
                handler.setFormatter(file_formatter)
                handler.name = output_file  # 纪录到logging._handlers
        else:
            handler = logging._handlers["console_detail"]
        logger.addHandler(handler)

        if level:
            logger.setLevel(level)
        # else:  延用handler的Level，或追溯root的Level

    return logger

getLogger = make_logger


if __name__ == "__main__":
    # 预定义logger
    logger = make_logger("console")

    # 创建新的logger
    logging.basicConfig(level=10)  # 更改全局默认的Level，仅用于未指定Level的logger对象
    logger2 = make_logger()  # 默认name=curr_module, output_file=False

    # 写入log日志文件
    logger3 = make_logger(output_file="new.log")

    # 不同的模块可写入同一日志，但logger对象不同
    logger4 = make_logger("logger4", output_file="new.log")
    logger4.setLevel(logging.DEBUG)


    # 其他常用操作

    # 常用的对象
    _manager = logging.Logger.manager  # 纪录了全部的logger对象
    _root = logging.Logger.root  # 即logging.root：Logger.root = root

    # 查询basicConfig的Level（也就是root.level)
    print(logging.root.level)

    logging.disable(level=10)  # Disable all logging calls of severity 'level' and below.