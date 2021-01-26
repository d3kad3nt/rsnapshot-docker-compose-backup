import configparser
import os
import re
from typing import Dict, Tuple, List

from src.AbstractConfig import AbstractConfig
from src.utils import CaseInsensitiveRe

folder = None


def set_folder(path: str):
    global folder
    folder = path


class DefaultConfig(AbstractConfig):
    __instance = None
    predefined_actions = "predefined_actions"
    predefined_actions_action = "actions"
    predefined_actions_command = "command"
    predefined_actions_step = "step"
    defaultConfig = "default_config"
    defaultConfigName = "backup.ini"
    defaultConfigFolder = "sdfasdfö"

    actions: Dict[str, List[Tuple[str, str]]] = {}

    @staticmethod
    def get_instance():
        if DefaultConfig.__instance is None:
            DefaultConfig()
        return DefaultConfig.__instance

    def __init__(self):
        if DefaultConfig.__instance is not None:
            raise Exception("This class is a singelton!")
        self.filename = os.path.join(folder, self.defaultConfigName)
        if not os.path.isfile(self.filename):
            self._create_default_config()
        super().__init__(self.filename, self.defaultConfig)
        self._load_predefined_actions()
        DefaultConfig.__instance = self

    def _create_default_config(self):
        with open(self.filename, 'w') as configfile:
            configfile.write(defaultConfigContent)

    def setting(self, name: str) -> str:
        return self.settings[name.lower()]

    def get_step(self, step: str) -> str:
        return self.backupSteps.get(step, "")

    def _load_predefined_actions(self):
        config_file = configparser.ConfigParser(allow_no_value=True)
        config_file.SECTCRE = CaseInsensitiveRe(re.compile(r"\[ *(?P<header>[^]]+?) *]"))
        config_file.read(self.defaultConfigName)
        sub_actions: List[Tuple[str, str]] = []
        for section in config_file.sections():
            if section.startswith(self.predefined_actions):
                action_name = section[len(self.predefined_actions + "."):]
                if config_file.has_option(section, self.predefined_actions_action):
                    sub_actions.append((section, action_name))
                command = config_file.get(section, self.predefined_actions_command, fallback=None)
                if command:
                    step = config_file.get(section, self.predefined_actions_step, fallback="backup")
                    self.actions[action_name] = [(step, command)]
        for section, action_name in sub_actions:
            if not self.actions.get(action_name):
                self.actions[action_name] = []
            actions = config_file.get(section, self.predefined_actions_action)
            for action in actions.split(" "):
                self.actions[action_name].extend(self.actions[action.lower().strip(",")])

    def get_action(self, name: str) -> (str, str):
        return self.actions[name]


defaultConfigContent = """
#This is the default config of the rsnapshot-docker-compose-backup program.

#This section can contain rsnapshot commands that are executed in the different steps of the container backup
[{default_config}]
#Example:
#run_backup=backup_script   echo "Hello" > helloWorld   test/

#This section contains settings that are used by the backup
[{default_config_settings}]
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
{command} = backup\\t$volumes.path\\t$backupPrefixFolder/$containerName/$volumes.name
{step} = backup

[{predefined_actions}.yamlBackup]
{command} = backup\\t$containerFolder/docker-compose.yml\\t$backupPrefixFolder/$containerName/docker-compose.yml
{step} = runtime_backup

[{predefined_actions}.imageBackup]
{command} = backup_script\\tdocker image save $image -o $containerName_image.tar\\t$backupPrefixFolder/$containerName/
{step} = runtime_backup

[{predefined_actions}.logBackup]
{command} = backup_script\\tdocker logs $containerName > $containerName_logs.log\\t$backupPrefixFolder/$containerName/
{step} = backup

[{predefined_actions}.stopContainer]
{actions} = stopContainer_stop, stopContainer_start

[{predefined_actions}.stopContainer_stop]
{command} = backup-exec\\tdocker-compose stop
{step} = stop

[{predefined_actions}.stopContainer_start]
{command} = backup-exec\\tdocker-compose start
{step} = restart""".format(
    default_config=DefaultConfig.defaultConfig,
    default_config_settings=DefaultConfig._settings_name(DefaultConfig.defaultConfig),
    default_config_actions=DefaultConfig._actions_name(DefaultConfig.defaultConfig),
    predefined_actions=DefaultConfig.predefined_actions,
    actions=DefaultConfig.predefined_actions_action,
    command=DefaultConfig.predefined_actions_command,
    step=DefaultConfig.predefined_actions_step
)