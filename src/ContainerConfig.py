from typing import NoReturn, Set, Dict

from src.AbstractConfig import AbstractConfig
from src.DefaultConfig import DefaultConfig


class ContainerConfig(AbstractConfig):

    def __init__(self, container):
        self.defaultConfig: DefaultConfig = DefaultConfig.get_instance()
        super().__init__(container.file_name, container.name)
        self.vars["$serviceName"] = container.name
        self.vars["$containerID"] = container.container_id
        self.vars["$projectFolder"] = container.folder
        self.vars["$volumes"] = container.volumes
        self.vars["$image"] = container.image
        self.vars["$projectName"] = container.project_name
        self.add_action_content()

    def _all_vars(self):
        variables = {}
        variables.update(self.defaultConfig.vars)
        variables.update(self.vars)
        return variables

    def output(self) -> NoReturn:
        for step in self.backupOrder:
            backup_action = self.get_step(step)
            if backup_action:
                print("#{}".format(step))
                for line in backup_action.splitlines():
                    script_command = self._resolve_vars(line, self._all_vars()).strip("\n")
                    single_commands = []
                    if "\n" in script_command:
                        single_commands = script_command.split("\n")
                    else:
                        single_commands.append(script_command)
                    for command in single_commands:
                        self._logTime()
                        print(command)
        self._logTime()

    def _logTime(self):
        log_time = self.defaultConfig.settings["logTime"]
        if log_time:
            print("backup_exec\t/bin/date +%s")


    def get_step(self, step: str) -> str:
        if self.backupSteps.get(step, ""):
            return self.backupSteps.get(step, "")
        else:
            return self.defaultConfig.get_step(step)

    def get_enabled_actions(self) -> Dict[str, bool]:
        merged_dict = self.defaultConfig.enabled_actions.copy()
        merged_dict.update(self.enabled_actions)
        return merged_dict

    def add_action_content(self):
        for action, enabled in sorted(self.get_enabled_actions().items()):
            if enabled:
                commands = self.defaultConfig.get_action(action)
                for step in commands:
                    self.backupSteps[step] += commands[step].strip() + "\n"
