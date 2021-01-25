import configparser
import os
import re
from abc import ABC, abstractmethod
from typing import Set, Dict

from src.utils import CaseInsensitiveRe
from src.volume import Volume


class AbstractConfig(ABC):

    actionSection = "actions"
    settingSection = "settings"

    def __init__(self, config_path: str, name: str):
        self.enabled_actions: Dict[str, bool] = {}
        self.settings: Dict[str, str] = {}
        self.backupSteps = {
            "runtime_backup": "",
            "pre_stop": "",
            "stop": "",
            "pre_backup": "",
            "backup": "",
            "post_backup": "",
            "restart": "",
            "post_restart": "",
        }
        self._load_config_file(config_path, name)
        self.name = name
        self._init_vars(config_path)

    def _init_vars(self, config_path: str):
        self.vars = {"$containerConfigDir": config_path,
                     "$volumeRootDir":      self.setting_or_default("volumeRootDir"),
                     "$backupPrefixFolder": self.setting_or_default("backupPrefixFolder", ".")}

    def _load_config_file(self, config_path: str, section_name: str):
        section_name = section_name.lower()
        config_file = configparser.ConfigParser(allow_no_value=True)
        config_file.SECTCRE = CaseInsensitiveRe(re.compile(r"\[ *(?P<header>[^]]+?) *]"))
        if os.path.isfile(config_path):
            config_file.read(config_path)
            if not config_file.sections():
                raise Exception("The Config for {} has no Sections".format(config_path))
            if not config_file.has_section(section_name):
                raise Exception("The Config for {} has no Section with the name of the Container ({})".
                                format(config_path, section_name))
        for step in self.backupSteps.keys():
            if config_file.has_option(section_name, step):
                self.backupSteps[step] = config_file.get(section_name, step).strip()+"\n"
        setting_section = self._settings_name(section_name)
        if config_file.has_section(setting_section):
            for setting in config_file.options(setting_section):
                self.settings[setting] = config_file.get(setting_section, setting)
        actions_section = self._actions_name(section_name)
        if config_file.has_section(actions_section):
            for action in config_file.options(actions_section):
                val = config_file.get(actions_section, action)
                use = val is None or val.lower() in ["true"]
                self.enabled_actions[action] = use

    def _resolve_vars(self, cmd: str) -> str:
        for var in self.vars:
            if var in cmd:
                replace_function = _replace_var.get(type(self.vars[var]))
                cmd = replace_function(cmd, var, self.vars[var])
        return cmd

    @abstractmethod
    def setting(self, name: str) -> str:
        pass

    def has_setting(self, name: str):
        try:
            self.setting(name)
            return True
        except Exception:
            return False

    def setting_or_default(self, name: str, default_val: str = ""):
        try:
            return self.setting(name)
        except Exception:
            return default_val

    @abstractmethod
    def get_step(self, step: str) -> str:
        pass

    @staticmethod
    def _create_subsection(super_section: str, sub_section: str):
        return "{}.{}".format(super_section, sub_section)

    @staticmethod
    def _settings_name(section_name: str) -> str:
        return AbstractConfig._create_subsection(section_name, AbstractConfig.settingSection)

    @staticmethod
    def _actions_name(section_name: str) -> str:
        return AbstractConfig._create_subsection(section_name, AbstractConfig.actionSection)




def _replace_list(cmd: str, var: str, val: list):
    result = ""
    for i in val:
        result += _replace_var[type(i)](cmd, var, i)
    return result


def _replace_str(cmd: str, var: str, val: str):
    return cmd.replace(var, val)


def _replace_volume(cmd: str, var: str, val: Volume):
    tmp = cmd.replace(var + ".name", val.name)
    tmp = tmp.replace(var + ".path", val.path)
    tmp = tmp.replace(var, val.path)
    return tmp + "\n"


_replace_var = {
    list: _replace_list,
    str: _replace_str,
    Volume: _replace_volume
}
