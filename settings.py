###############################################################################
# Name:         settings
# Usage:        settings = IniConfigSettings()
#               settings.load(rpath2curr("config/settings.ini")
# Author:       Bright Li
# Modified by:
# Created:      2020-01-06
# Version:      [0.1.0]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

import json
from configparser import ConfigParser, Error
import os.path
from .base import rpath2curr

class SettingsBase:
    def __init__(self):
        self.path = None
        self.data = {}

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        if key in self.data:
            return self.data[key]
        return default

    def load(self, path_config):
        pass

    def save(self, path_save_as=None):
        pass


class JsonSettings(SettingsBase):
    def load(self, path_config):
        assert os.path.exists(path_config), f"Settings导入失败：不存在配置文件【{path_config}】"
        with open(path_config, 'r') as fp:
            self.data = json.load(fp)
        self.path = path_config

    def save(self, path_save_as=None):
        if not path_save_as:
            assert self.path, "无有效的配置文件存储路径"
            path_save_as = self.path
        with open(path_save_as, 'w') as fp:
            json.dump(self.data, fp)


class IniConfigSettings(ConfigParser):  # SettingsBase
    def __init__(self):
        super().__init__()
        self.path = None

    # def get(self, section, option, default=None):
    #     if not self.has_option(section, option):
    #         return default
    #     try:
    #         print(section, option, default)
    #         return super().get(section, option)  raw=True!
    #     except KeyError:
    #         return default

    def load(self, path_config):
        assert os.path.exists(path_config), f"Settings导入失败：不存在配置文件【{path_config}】"
        self.read(path_config, encoding="utf-8")
        self.path = path_config

    def save(self, path_save_as=None):
        if not path_save_as:
            assert self.path, "无有效的配置文件存储路径"
            path_save_as = self.path
        with open(path_save_as, 'w') as fp:
            self.write(fp)

    def get(self, section, option, default=None):
        try:
            return super().get(section, option, raw=True)
        except Error:
            return default


if __name__ == "__test_singleton__":
    base = SettingsBase()
    print(base._instance)

    derive = IniConfigSettings()
    print(derive._instance)

    # derive._instance = [2,3]  # 将类成员改为对象成员，而不影响基类
    derive._instance[0] = -1  # 将改写所有的class._instance的list
    print(derive._instance)
    print(base._instance)


if __name__ == "__main__":
    from .base import singleton

    @singleton
    class MyProjectSetting(IniConfigSettings):
        def __init__(self):
            super().__init__()
            print("singleton init...")
            # 载入项目固定路径的配置，实例化时则无需关心是否load
            # self.load("./config.ini")

    settings = MyProjectSetting()
    settings2 = MyProjectSetting()
    print(settings is settings2)