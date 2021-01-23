import configparser
import os
import re
from typing import Dict, Tuple

from src.AbstractConfig import AbstractConfig
from src.utils import CaseInsensitiveRe


class DefaultConfig(AbstractConfig):
    predefined_actions = "predefined_actions"
    defaultConfig = "default_config"
    defaultConfigName = "backup.ini"
    actions: Dict[str, Tuple[str, str]] = {}

    def __init__(self):
        if not os.path.isfile(self.defaultConfigName):
            self._create_default_config()
        super().__init__(self.defaultConfigName, self.defaultConfig)
        self._load_predefined_actions()

    @staticmethod
    def _create_default_config():
        default_config = configparser.ConfigParser()
        default_config.read_dict(
            {
                DefaultConfig.defaultConfig: {
                    "PreBackup": "backup-exec docker-compose stop",
                    "PostBackup": "backup-exec docker-compose start"},
                DefaultConfig._settings_name(DefaultConfig.defaultConfig): {
                    "volumeRootDir": "/var/lib/docker/volumes/",
                    "backupPrefixFolder": "/var/lib/docker/volumes/"},
                DefaultConfig._actions_name(DefaultConfig.defaultConfig): {
                    "volumeBackup": "true",
                    "yamlBackup": "true"
                },
                DefaultConfig.predefined_actions: {
                    "volumeBackup": "backup    $volumes.path    $backupPrefixFolder/$containerName/$volumes.name",
                    "yamlBackup": "backup   $containerFolder/docker-compose.yml $backupPrefixFolder/$containerName/docker-compose.yml"
                }

            }
        )
        with open(DefaultConfig.defaultConfigName, 'w') as configfile:
            default_config.write(configfile)

    def setting(self, name: str) -> str:
        return self.settings[name.lower()]

    def get_step(self, step: str) -> str:
        return self.backupSteps.get(step, "")

    def _load_predefined_actions(self):
        config_file = configparser.ConfigParser(allow_no_value=True)
        config_file.SECTCRE = CaseInsensitiveRe(re.compile(r"\[ *(?P<header>[^]]+?) *]"))
        config_file.read(self.defaultConfigName)
        step_postfix = "_step"
        if config_file.has_section(self.predefined_actions):
            for action in config_file.options(self.predefined_actions):
                if step_postfix not in action:
                    step = "backup"
                    if config_file.has_option(self.predefined_actions, action+step_postfix):
                        step = config_file.get(self.predefined_actions, action+step_postfix)
                    self.actions[action] = (step, config_file.get(self.predefined_actions, action))

    def get_action(self, name: str) -> (str, str):
        return self.actions[name]
