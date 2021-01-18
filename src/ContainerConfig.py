from typing import NoReturn

from src import docker
from src.AbstractConfig import AbstractConfig
from src.DefaultConfig import DefaultConfig


class ContainerConfig(AbstractConfig):
    defaultConfig: DefaultConfig = DefaultConfig()

    def __init__(self, config_path: str, container_name: str):
        super().__init__(config_path, container_name)
        self.vars["$containerName"] = container_name
        self.vars["$volumes"] = docker.volumes(container_name)

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