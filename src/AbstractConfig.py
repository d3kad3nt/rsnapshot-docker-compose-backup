import configparser
import os
import re
from abc import ABC, abstractmethod

from src.utils import CaseInsensitiveRe


class AbstractConfig(ABC):

    settingSection = "settings"

    def __init__(self, config_path: str, name: str):
        self.settings = {}
        self.backupSteps = {
            "RuntimeBackup": "",
            "PreStop": "",
            "Stop": "",
            "PreBackup": "",
            "Backup": "",
            "PostBackup": "",
            "Restart": "",
            "PostRestart": "",
        }
        self._load_config_file(config_path, name)
        self.name = name
        self.vars = {"$volumeRootDir": self.setting("volumeRootDir"),
                     "$containerConfigDir": config_path}

    def _load_config_file(self, config_path: str, section_name: str):
        config_file = configparser.ConfigParser()
        config_file.SECTCRE = CaseInsensitiveRe(re.compile(r"\[ *(?P<header>[^]]+?) *]"))
        if os.path.isfile(config_path):
            config_file.read([config_path])
            if not config_file.sections():
                raise Exception("The Config for {} has no Sections".format(config_path))
            if not config_file.has_section(section_name):
                raise Exception("The Config for {} has no Section with the name of the Container ({})".
                                format(config_path, section_name))
        else:
            print("#No specific config for {}.".format(section_name))

        for step in self.backupSteps.keys():
            if config_file.has_option(section_name, step):
                self.backupSteps[step] = config_file.get(section_name, step)
        setting_section = self._settings_name(section_name)
        if config_file.has_section(setting_section):
            for setting in config_file.options(setting_section):
                self.settings[setting] = config_file.get(setting_section, setting)

    def _resolve_vars(self, cmd: str) -> str:
        for var in self.vars:
            if var in cmd:
                if type(self.vars[var]) is list:
                    res = ""
                    for val in self.vars[var]:
                        res += cmd.replace(var, val) + "\n"
                    cmd = res
                else:
                    cmd = cmd.replace(var, self.vars[var])
        return cmd

    @abstractmethod
    def setting(self, name: str) -> str:
        pass

    @abstractmethod
    def get_step(self, step: str) -> str:
        pass

    @staticmethod
    def _settings_name(section_name: str) -> str:
        return section_name + "." + AbstractConfig.settingSection