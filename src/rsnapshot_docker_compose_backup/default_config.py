import configparser
import os
from pathlib import Path
import re
from typing import Optional

from rsnapshot_docker_compose_backup import global_values
from rsnapshot_docker_compose_backup.abstract_config import AbstractConfig
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
        with open(self.filename, "w", encoding="UTF-8") as config_file:
            config_file.write(defaultConfigContent)

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
                    if config_file.has_option(section, step):
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


defaultConfigContent = """
#This is the default config of the rsnapshot-docker-compose-backup program.

#This section can contain rsnapshot commands that are executed in the different steps of the container backup
[{default_config}]
#Example:
#run_backup=backup_script   echo "Hello" > helloWorld   test/

#This section contains settings that can be set. This section can only be used in the default config.
[{default_config_settings}]
#This outputs the Start and End Times for each backup command to the log. 
#Rsnapshot doesn't log timestamps
logTime = true

[{default_config_vars}]
#This setting corresponds to the var with the same name and can be used as a prefix in the folder path
backupprefixfolder = .

#This Section controls which actions should be enabled
[{default_config_actions}]
#This action stops the container before copying the volumes and starts it after it finished.
stopcontainer = true

#This action backups all volumes of the container
volumebackup = true

#This action saves the docker-compose.yml
yamlbackup = true
imagebackup = true

#The following actions are disabled by default
logbackup = false
projectDirBackup = false

#The following is the definition of actions that can be used in the backup

[{actions}.volumeBackup]
backup = backup\t$volumes.path\t$backupPrefixFolder/$serviceName/$volumes.name

[{actions}.yamlBackup]
runtime_backup = backup\t$projectFolder\t$backupPrefixFolder/$serviceName/yaml\t+rsync_long_args=--include=*.yml,+rsync_long_args=--include=*.yaml

[{actions}.projectDirBackup]
backup = backup\t$projectFolder\t$backupPrefixFolder/$serviceName/projectDir

[{actions}.imageBackup]
runtime_backup = backup_script\t/usr/bin/docker image save $image -o $serviceName_image.tar\t$backupPrefixFolder/$serviceName/image

[{actions}.logBackup]
backup = backup_script\t/usr/bin/docker logs $containerID > $serviceName_logs.log 2>&1\t$backupPrefixFolder/$serviceName/log

[{actions}.stopContainer]
stop = backup_exec\tcd $projectFolder; /usr/bin/docker-compose stop
restart = backup_exec\tcd $projectFolder; /usr/bin/docker-compose start

""".format(
    default_config=DefaultConfig.defaultConfig,
    default_config_actions=DefaultConfig.actions_name(DefaultConfig.defaultConfig),
    default_config_vars=DefaultConfig.vars_name(DefaultConfig.defaultConfig),
    actions=DefaultConfig.actionSection,
    default_config_settings=DefaultConfig.settingsSection,
)
