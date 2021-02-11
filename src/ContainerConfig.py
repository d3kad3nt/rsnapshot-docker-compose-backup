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
                    print(self._resolve_vars(line, self._all_vars()).strip("\n"))

    def setting(self, name: str) -> str:
        if name.lower() in self.settings:
            return self.settings[name.lower()]
        else:
            return self.defaultConfig.setting(name)

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
        for action, enabled in self.get_enabled_actions().items():
            if enabled:
                commands = self.defaultConfig.get_action(action)
                for step, command in commands:
                    self.backupSteps[step] += command.strip() + "\n"
