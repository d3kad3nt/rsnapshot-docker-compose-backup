from __future__ import annotations

import configparser
import os
import re
from abc import ABC, abstractmethod
from typing import NoReturn


class CaseInsensitiveRe:
    def __init__(self, regex):
        self.regex = regex

    def match(self, text):
        m = self.regex.match(text)
        if m:
            return CaseInsensitiveMatch(m)
        return None


class CaseInsensitiveMatch:
    def __init__(self, match):
        self.match = match

    def group(self, name):
        return self.match.group(name).lower()


class AbstractConfig(ABC):
    backupSteps = {
        "RuntimeBackup": "",
        "PreStop": "",
        "Stop": "",
        "PreBackup": "",
        "Backup": "",
        "PostBackup": "",
        "Restart": "",
        "PostRestart": "",
    }

    settings = {}

    settingSection = "settings"

    vars = {}

    def __init__(self, config_path: str, name: str):
        self._load_config_file(config_path, name)
        self.name = name
        self.vars["$volumeRootDir"] = self.setting("volumeRootDir")
        self.vars["$containerName"] = name
        self.vars["$containerConfigDir"] = config_path

    def _load_config_file(self, config_path: str, section_name: str):
        config_file = configparser.ConfigParser()
        config_file.SECTCRE = CaseInsensitiveRe(re.compile(r"\[ *(?P<header>[^]]+?) *]"))
        if os.path.isfile(config_path):
            config_file.read([config_path])
            print(config_file.sections())
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

    def _parse(self, cmd: str) -> str:
        cmd = self._resolve_vars(cmd)
        cmd = self._resolve_commands(cmd)
        return cmd

    def _resolve_vars(self, cmd: str) -> str:
        for var in self.vars:
            cmd = cmd.replace(var, self.vars[var])
        return cmd

    @staticmethod
    def _resolve_commands(cmd: str) -> str:
        if cmd.startswith("cmd"):
            cmd = "backup_exec\t" + cmd[3:].strip()
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


class DefaultConfig(AbstractConfig):
    defaultActions = "default_actions"
    defaultConfigName = "backup.ini"

    def __init__(self):
        if not os.path.isfile(self.defaultConfigName):
            self._create_default_config()
        super().__init__(self.defaultConfigName, self.defaultActions)

    @staticmethod
    def _create_default_config():
        default_config = configparser.ConfigParser()
        default_config.read_dict(
            {
                DefaultConfig.defaultActions: {
                    "PreBackup": "cmd docker-compose stop",
                    "Backup": "backup    $volumes    $backupPrefixFolder/$containerName/$volumes",
                    "PostBackup": "cmd docker-compose start"},
                DefaultConfig._settings_name(DefaultConfig.defaultActions): {
                    "volumeRootDir": "/var/lib/docker/volumes/",
                    "backupPrefixFolder": "/var/lib/docker/volumes/"}
            }
        )
        with open(DefaultConfig.defaultConfigName, 'w') as configfile:
            default_config.write(configfile)

    def setting(self, name: str) -> str:
        return self.settings[name.lower()]

    def get_step(self, step: str) -> str:
        return self.backupSteps.get(step, "")


class ContainerConfig(AbstractConfig):
    defaultConfig: DefaultConfig = DefaultConfig()

    def __init__(self, config_path: str, container_name: str):
        super().__init__(config_path, container_name)

    def output(self) -> NoReturn:
        for step in self.backupSteps:
            backup_action = self.get_step(step)
            if backup_action:
                print(f"#{step}")
                for line in backup_action.splitlines():
                    print(self._parse(line))

    def setting(self, name: str) -> str:
        if self.settings[name.lower()]:
            return self.settings[name.lower()]
        else:
            return self.defaultConfig.setting(name)

    def get_step(self, step: str) -> str:
        if self.backupSteps.get(step, ""):
            return self.backupSteps.get(step, "")
        else:
            return self.defaultConfig.get_step(step)
