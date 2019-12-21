
###############################################################################
# Name:         glob
# Usage:        from mylib.glob import GlobMnger
# Author:       Bright Li
# Modified by:
# Created:      2019-12-11
# Version:      [0.1.5]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

from .base import singleton

class VariableNoExist(Exception):
    def __init__(self, errmsg):
        super().__init__()
        self.value = errmsg

    def __str__(self):
        return self.value


@singleton
class GlobalObjectManager:
    def __init__(self):
        self.dict_variable = {}  # variable_name: variable
        self.dict_callable = {}  # call_name: callable_func

    def register(self, keyword, variable, isCall=False, forced=False):
        if not forced and self.check(keyword, isCall):
            # self._listAll()
            raise Exception("GlobalObjectManager::register() -->> 【{}】已存在全局列表中，请勿重复注册".format(keyword))
        dict_ = self.dict_callable if isCall else self.dict_variable
        dict_[keyword] = variable

    def register_call(self, keyword, obj_call):
        self.register(keyword, obj_call, True)

    def check(self, var_name, isCall=False):
        dict_ = self.dict_callable if isCall else self.dict_variable
        return var_name in dict_

    def call(self, keyword, *args, **kwargs):
        if not self.check(keyword, True):
            raise VariableNoExist("CallableManager::call() -->> 未注册的函数调用：【{}】".format(keyword))
        return self.dict_callable[keyword](*args, **kwargs)

    def get(self, keyword):
        if not self.check(keyword):
            raise VariableNoExist("GlobalObjectManager::get() -->> 未注册的全局变量：【{}】".format(keyword))
        return self.dict_variable[keyword]

    def override(self, keyword, new_var):
        if not self.check(keyword):
            raise VariableNoExist("VariableManager::get() -->> 未注册的全局变量：【{}】".format(keyword))
        self.dict_variable[keyword] = new_var
        # or, you can get() the keyword, and modify the value directly
        # this way maybe more effective, for the value of list/dict...

    def _listAll(self):
        from pprint import pprint
        print("GlobalObjectManager 目前存在以下全局变量：")
        pprint(self.dict_variable)
        print("以及全局函数：")
        pprint(self.dict_callable)

    # def pop(self, keyword):
    #     raise Exception("GlobalObjectManager::pop() -->> 全局对象，不支持删除操作")

    # 其他接口，请直接调用 self.dict_xxx 进行操作（非常规，不推荐）

g = GlobalObjectManager()  # 全局单例
