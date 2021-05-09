import configparser
import os
import re
from typing import Dict, Tuple, List

import src.global_values
from src.AbstractConfig import AbstractConfig
from src.utils import CaseInsensitiveRe


class DefaultConfig(AbstractConfig):
    __instance = None
    predefined_actions = "predefined_actions"
    predefined_actions_action = "actions"
    defaultConfig = "default_config"
    defaultConfigName = "backup.ini"

    actions: Dict[str, Dict[str, str]] = {}

    @staticmethod
    def get_instance():
        if DefaultConfig.__instance is None:
            DefaultConfig()
        return DefaultConfig.__instance

    def __init__(self):
        if DefaultConfig.__instance is not None:
            raise Exception("This class is a singelton!")
        if src.global_values.config_file != "":
            self.filename = src.global_values.config_file
        else:
            self.filename = os.path.join(src.global_values.folder, self.defaultConfigName)
        if not os.path.isfile(self.filename):
            self._create_default_config()
        super().__init__(self.filename, self.defaultConfig)
        self._load_predefined_actions()
        DefaultConfig.__instance = self

    def _create_default_config(self):
        with open(self.filename, 'w') as configfile:
            configfile.write(defaultConfigContent)

    def get_step(self, step: str) -> str:
        return self.backupSteps.get(step, "")

    def _load_predefined_actions(self):
        config_file = configparser.ConfigParser(allow_no_value=True)
        config_file.SECTCRE = CaseInsensitiveRe(re.compile(r"\[ *(?P<header>[^]]+?) *]"))
        config_file.read(self.filename)
        sub_actions: List[Tuple[str, str]] = []
        for section in config_file.sections():
            if section.startswith(self.predefined_actions):
                action_name = section[len(self.predefined_actions + "."):]
                if config_file.has_option(section, self.predefined_actions_action):
                    sub_actions.append((section, action_name))
                commands = {}
                for step in self.backupSteps:
                    if config_file.has_option(section, step):
                        commands[step] = config_file.get(section, step).strip() + "\n"
                if commands:
                    self.actions[action_name] = commands
        for section, action_name in sub_actions:
            if not self.actions.get(action_name):
                self.actions[action_name] = {}
            actions = config_file.get(section, self.predefined_actions_action)
            for action in actions.split(" "):
                self.actions[action_name].update(self.actions[action.lower().strip(",")])

    def get_action(self, name: str) -> (str, str):
        return self.actions[name]


defaultConfigContent = """
#This is the default config of the rsnapshot-docker-compose-backup program.

#This section can contain rsnapshot commands that are executed in the different steps of the container backup
[{default_config}]
#Example:
#run_backup=backup_script   echo "Hello" > helloWorld   test/

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

#The following is the definition of actions that can be used in the backup

[{predefined_actions}.volumeBackup]
backup = backup\t$volumes.path\t$backupPrefixFolder/$serviceName/$volumes.name

[{predefined_actions}.yamlBackup]
runtime_backup = backup\t$projectFolder\t$backupPrefixFolder/$serviceName/yaml\t+rsync_long_args=--include=*.yml,+rsync_long_args=--include=*.yaml

[{predefined_actions}.projectDirBackup]
backup = backup\t$projectFolder\t$backupPrefixFolder/$serviceName/projectDir

[{predefined_actions}.imageBackup]
runtime_backup = backup_script\t/usr/bin/docker image save $image -o $serviceName_image.tar\t$backupPrefixFolder/$serviceName/image

[{predefined_actions}.logBackup]
backup = backup_script\t/usr/bin/docker logs $containerID > $serviceName_logs.log\t$backupPrefixFolder/$serviceName/log

[{predefined_actions}.stopContainer]
#{actions} = stopContainer_stop, stopContainer_start
stop = backup_exec\tcd $projectFolder; /usr/bin/docker-compose stop
restart = backup_exec\tcd $projectFolder; /usr/bin/docker-compose start

""".format(
    default_config=DefaultConfig.defaultConfig,
    default_config_actions=DefaultConfig._actions_name(DefaultConfig.defaultConfig),
    default_config_vars=DefaultConfig._vars_name(DefaultConfig.defaultConfig),
    predefined_actions=DefaultConfig.predefined_actions,
    actions=DefaultConfig.predefined_actions_action,
)
