import configparser
import os
import re
from importlib import resources
from pathlib import Path
from typing import ClassVar, Optional

from rsnapshot_docker_compose_backup import global_values
from rsnapshot_docker_compose_backup.config.abstract_config import AbstractConfig
from rsnapshot_docker_compose_backup.utils.regex import CaseInsensitiveRe


class DefaultConfig(AbstractConfig):
    __instance: Optional["DefaultConfig"] = None
    default_config = "default_config"
    default_config_name = "backup.ini"
    settings_section = "settings"
    action_section = "actions"

    # Settings
    settings: ClassVar[dict[str, bool]] = {
        "logTime": True,
        "onlyRunning": True,
    }

    actions: ClassVar[dict[str, dict[str, str]]] = {}

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
            msg = "This class is a singleton!"
            raise RuntimeError(msg)
        if global_values.config_file is not None:
            self.filename: Path = global_values.config_file
        else:
            self.filename = global_values.folder / Path(
                self.default_config_name,
            )
        if not os.path.isfile(self.filename):
            self._create_default_config()
        super().__init__(self.filename, self.default_config)
        self._load_actions()
        self._load_settings()

    def _create_default_config(self) -> None:
        with resources.open_text(
            "rsnapshot_docker_compose_backup.config", "backup.ini"
        ) as default_backup_ini:
            default_config = default_backup_ini.read().format(
                default_config=self.default_config,
                default_config_actions=self.actions_name(self.default_config),
                default_config_vars=self.vars_name(self.default_config),
                actions=self.action_section,
                default_config_settings=self.settings_section,
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
            if section.startswith(self.action_section):
                action_name = section[len(self.action_section + ".") :]
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
            if config_file.has_option(self.settings_section, setting):
                self.settings[setting] = config_file.getboolean(
                    self.settings_section, setting
                )
                # print(f"{setting} is set to {self.settings[setting]}")

    def get_action(self, name: str) -> Dict[str, str]:
        return self.actions[name]
