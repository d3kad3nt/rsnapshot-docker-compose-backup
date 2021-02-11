import configparser
import os
import re
from abc import ABC, abstractmethod
from typing import Dict

from src.utils import CaseInsensitiveRe
from src.volume import Volume


class AbstractConfig(ABC):

    actionSection = "actions"
    settingSection = "settings"
    varSection = "vars"
    backupOrder = [
        "runtime_backup",
        "pre_stop",
        "stop",
        "pre_backup",
        "backup",
        "post_backup",
        "restart",
        "post_restart",
    ]

    def __init__(self, config_path: str, name: str):
        self.enabled_actions: Dict[str, bool] = {}
        self.settings: Dict[str, str] = {}
        self.backupSteps = {}
        self.vars = {}
        for step in self.backupOrder:
            self.backupSteps[step] = ""
        self._load_config_file(config_path, name)
        self.name = name
        self._init_vars(config_path)

    def _init_vars(self, config_path: str):
        self.vars["$dockerComposeFile"] = config_path
        if "$backupPrefixFolder" not in self.vars:
            self.vars["$backupPrefixFolder"] = "."

    def _load_config_file(self, config_path: str, section_name: str):
        section_name = section_name.lower()
        config_file = configparser.ConfigParser(allow_no_value=True)
        config_file.SECTCRE = CaseInsensitiveRe(re.compile(r"\[ *(?P<header>[^]]+?) *]"))
        if os.path.isfile(config_path):
            config_file.read(config_path)
            if not config_file.sections():
                raise Exception("The Config for {} has no Sections".format(config_path))
        for step in self.backupSteps.keys():
            if config_file.has_option(section_name, step):
                self.backupSteps[step] = config_file.get(section_name, step).strip()+"\n"
        setting_section = self._settings_name(section_name)
        if config_file.has_section(setting_section):
            for setting in config_file.options(setting_section):
                self.settings[setting.lower()] = config_file.get(setting_section, setting)
        actions_section = self._actions_name(section_name)
        if config_file.has_section(actions_section):
            for action in config_file.options(actions_section):
                val = config_file.get(actions_section, action)
                use = val is None or val.lower() in ["true"]
                self.enabled_actions[action] = use
        vars_section = self._vars_name(section_name)
        if config_file.has_section(vars_section):
            for var in config_file.options(vars_section):
                val = config_file.get(vars_section, var)
                self.vars["${}".format(var)] = val

    def _resolve_vars(self, cmd: str, variables: Dict[str, str]) -> str:
        for var in variables.keys():
            if var.lower() in cmd.lower():
                replace_function = _replace_var.get(type(variables[var]))
                cmd = replace_function(cmd, var, variables[var])
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

    @staticmethod
    def _vars_name(section_name: str) -> str:
        return AbstractConfig._create_subsection(section_name, AbstractConfig.varSection)


def ireplace(old, new, text):
    idx = 0
    while idx < len(text):
        index_l = text.lower().find(old.lower(), idx)
        if index_l == -1:
            return text
        text = text[:index_l] + new + text[index_l + len(old):]
        idx = index_l + len(new)
    return text


def _replace_list(cmd: str, var: str, val: list):
    result = ""
    for i in val:
        result += _replace_var[type(i)](cmd, var, i) + "\n"
    return result


def _replace_str(cmd: str, var: str, val: str):
    return ireplace(var, val, cmd)


def _replace_volume(cmd: str, var: str, val: Volume):
    tmp = _replace_str(cmd, var + ".name", val.name)
    tmp = _replace_str(tmp,var + ".path", val.path)
    tmp = _replace_str(tmp,var, val.path)
    return tmp


_replace_var = {
    list: _replace_list,
    str: _replace_str,
    Volume: _replace_volume
}
