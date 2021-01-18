import configparser
import os

from src.AbstractConfig import AbstractConfig


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