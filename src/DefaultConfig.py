import configparser
import os
import re
from typing import Dict, Tuple

from src.AbstractConfig import AbstractConfig
from src.utils import CaseInsensitiveRe


class DefaultConfig(AbstractConfig):
    predefined_actions = "predefined_actions"
    predefined_actions_command = "command"
    predefined_actions_step = "step"
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
                    "pre_backup": "backup-exec docker-compose stop",
                    "post_backup": "backup-exec docker-compose start"},
                DefaultConfig._settings_name(DefaultConfig.defaultConfig): {
                    "volumeRootDir": "/var/lib/docker/volumes/",
                    "backupPrefixFolder": "/var/lib/docker/volumes/"},
                DefaultConfig._actions_name(DefaultConfig.defaultConfig): {
                    "volumeBackup": "true",
                    "yamlBackup": "true",
                    "imageBackup": "true"
                },
                DefaultConfig._create_subsection(DefaultConfig.predefined_actions, "volumeBackup"): {
                    DefaultConfig.predefined_actions_command: "backup    $volumes.path    $backupPrefixFolder/$containerName/$volumes.name",
                    DefaultConfig.predefined_actions_step: "backup"
                },
                DefaultConfig._create_subsection(DefaultConfig.predefined_actions,  "yamlBackup"): {
                    DefaultConfig.predefined_actions_command: "backup   $containerFolder/docker-compose.yml $backupPrefixFolder/$containerName/docker-compose.yml",
                    DefaultConfig.predefined_actions_step: "runtime_backup"
                },
                DefaultConfig._create_subsection(DefaultConfig.predefined_actions,  "imageBackup"): {
                    DefaultConfig.predefined_actions_command: "backup_script	docker image save $image -o $containerName_image.tar    $backupPrefixFolder/$containerName/",
                    DefaultConfig.predefined_actions_step: "runtime_backup"
                },
                DefaultConfig._create_subsection(DefaultConfig.predefined_actions,  "logBackup"): {
                    DefaultConfig.predefined_actions_command: "backup_script docker logs $containerName > $containerName_logs.log    $backupPrefixFolder/$containerName/",
                    DefaultConfig.predefined_actions_step: "backup"
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
        for section in config_file.sections():
            if section.startswith(self.predefined_actions):
                action_name = section[len(self.predefined_actions + "."):]
                if not config_file.has_option(section, self.predefined_actions_command):
                    raise Exception("The action {} has to have a command".format(action_name))
                command = config_file.get(section, self.predefined_actions_command)
                step = "backup"
                if config_file.has_option(section, self.predefined_actions_step):
                    step = config_file.get(section, self.predefined_actions_step)
                self.actions[action_name] = (step, command)

    def get_action(self, name: str) -> (str, str):
        return self.actions[name]
