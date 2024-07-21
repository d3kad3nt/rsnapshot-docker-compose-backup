import configparser
from importlib import resources
import os
from pathlib import Path
import re
from typing import Optional

from rsnapshot_docker_compose_backup import global_values
from rsnapshot_docker_compose_backup.config.abstract_config import AbstractConfig
from rsnapshot_docker_compose_backup.utils import CaseInsensitiveRe


class DefaultConfig(AbstractConfig):
    __instance: Optional["DefaultConfig"] = None
    defaultConfig = "default_config"
    defaultConfigName = "backup.ini"
    settingsSection = "settings"
    actionSection = "actions"

    # Settings
    settings = {
        "logTime": True,
        "onlyRunning": True,
    }

    actions: dict[str, dict[str, str]] = {}

    @staticmethod
    def get_instance() -> "DefaultConfig":
        # print(f"Get Default Config, {DefaultConfig.__instance}")
        if DefaultConfig.__instance is None:
            DefaultConfig.__instance = DefaultConfig()
        return DefaultConfig.__instance

    @staticmethod
    def reset() -> None:
        DefaultConfig.__instance = None

    def __init__(self) -> None:
        if DefaultConfig.__instance is not None:
            raise Exception("This class is a singleton!")
        if global_values.config_file is not None:
            self.filename: Path = global_values.config_file
        else:
            self.filename = global_values.folder / Path(
                self.defaultConfigName,
            )
        if not os.path.isfile(self.filename):
            self._create_default_config()
        super().__init__(self.filename, self.defaultConfig)
        self._load_actions()
        self._load_settings()

    def _create_default_config(self) -> None:
        with resources.open_text(
            "rsnapshot_docker_compose_backup.config", "backup.ini"
        ) as default_backup_ini:
            default_config = default_backup_ini.read().format(
                default_config=self.defaultConfig,
                default_config_actions=self.actions_name(self.defaultConfig),
                default_config_vars=self.vars_name(self.defaultConfig),
                actions=self.actionSection,
                default_config_settings=self.settingsSection,
            )

            with open(self.filename, "w", encoding="UTF-8") as config_file:
                config_file.write(default_config)

    def get_step(self, step: str) -> str:
        return self.backup_steps.get(step, "")

    def _load_actions(self) -> None:
        config_file = configparser.ConfigParser(allow_no_value=True)
        config_file.SECTCRE = CaseInsensitiveRe(
            re.compile(r"\[ *(?P<header>[^]]+?) *]")
        )  # type: ignore
        config_file.read(self.filename)
        for section in config_file.sections():
            if section.startswith(self.actionSection):
                action_name = section[len(self.actionSection + ".") :]
                commands = {}
                for step in self.backup_steps:
                    if config_file.has_option(section.lower(), step):
                        commands[step] = config_file.get(section, step).strip() + "\n"
                if commands:
                    self.actions[action_name] = commands

    def _load_settings(self) -> None:
        config_file = configparser.ConfigParser(allow_no_value=True)
        config_file.SECTCRE = CaseInsensitiveRe(
            re.compile(r"\[ *(?P<header>[^]]+?) *]")
        )  # type: ignore
        config_file.read(self.filename)
        # print(f"filename {self.filename}")
        for setting in self.settings:
            if config_file.has_option(self.settingsSection, setting):
                self.settings[setting] = config_file.getboolean(
                    self.settingsSection, setting
                )
                # print(f"{setting} is set to {self.settings[setting]}")

    def get_action(self, name: str) -> dict[str, str]:
        return self.actions[name]
