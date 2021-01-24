from typing import NoReturn, Set, Dict

from src import docker
from src.AbstractConfig import AbstractConfig
from src.DefaultConfig import DefaultConfig


class ContainerConfig(AbstractConfig):
    defaultConfig: DefaultConfig = DefaultConfig()

    def __init__(self, container):
        super().__init__(container.file_name, container.name)
        self.vars["$containerName"] = container.name
        self.vars["$containerFolder"] = container.folder
        self.vars["$volumes"] = container.volumes
        self.add_action_content()

    def output(self) -> NoReturn:
        for step in self.backupSteps:
            backup_action = self.get_step(step)
            if backup_action:
                print(f"#{step}")
                for line in backup_action.splitlines():
                    print(self._resolve_vars(line))

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
                command = self.defaultConfig.get_action(action)
                self.backupSteps[command[0]] += command[1].strip("\n") + "\n"
