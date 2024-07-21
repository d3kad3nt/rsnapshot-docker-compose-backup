from pathlib import Path
from typing import Optional, Union

import os

from rsnapshot_docker_compose_backup.docker import docker
from rsnapshot_docker_compose_backup.structure.volume import Volume
from rsnapshot_docker_compose_backup.config.abstract_config import AbstractConfig
from rsnapshot_docker_compose_backup.config.default_config import DefaultConfig


class Container:
    folder: Path
    service_name: str
    config: "ContainerConfig"
    volumes: list[Volume]

    def __init__(
        self,
        folder: Path,
        service_name: str,
        container_name: str,
        container_id: str,
        running: bool,
    ):
        self.folder: Path = folder
        self.service_name = service_name
        self.container_name = container_name
        self.container_id = container_id
        self.project_name = os.path.basename(folder)
        self.image = docker.image(container_id)
        self.file_name: Path = self.folder / "backup.ini"
        self.volumes = docker.volumes(container_id)
        self.is_running = running
        self.config = ContainerConfig(self)

    def backup(self) -> str:
        result: list[str] = []
        output = self.config.output()
        if output is None:
            # print("output is none")
            return ""
        result.append(
            "##Start backup for compose project {} - service {}".format(
                self.project_name, self.service_name
            )
        )
        result.append(output)
        result.append(
            "##End backup for compose project {} - service {}".format(
                self.project_name, self.service_name
            )
        )
        result.append("")
        return "\n".join(result)

    def __str__(self) -> str:
        return "Container {} in folder {}".format(self.service_name, self.folder)

    def __repr__(self) -> str:
        return "Container {} in folder {}".format(self.service_name, self.folder)


class ContainerConfig(AbstractConfig):
    def __init__(self, container: "Container"):
        self.default_config: DefaultConfig = DefaultConfig.get_instance()
        super().__init__(container.file_name, container.service_name)
        self.vars["$serviceName"] = container.service_name
        self.vars["$containerID"] = container.container_id
        self.vars["$containerName"] = container.container_name
        self.vars["$projectFolder"] = str(container.folder)
        self.vars["$volumes"] = container.volumes
        self.vars["$image"] = container.image
        self.vars["$projectName"] = container.project_name
        self._is_running = container.is_running
        self.add_action_content()

    def _all_vars(self) -> dict[str, Union[str, list[Volume]]]:
        variables: dict[str, Union[str, list[Volume]]] = {}
        variables.update(self.default_config.vars)
        variables.update(self.vars)
        return variables

    def output(self) -> Optional[str]:
        if self.default_config.settings["onlyRunning"] and not self._is_running:
            return None
        result: list[str] = []

        for step in self.backupOrder:
            backup_action = self.get_step(step)
            if backup_action:
                result.append("#{}".format(step))
                for line in backup_action.splitlines():
                    script_command = self._resolve_vars(line, self._all_vars()).strip(
                        "\n"
                    )
                    single_commands: list[str] = []
                    if "\n" in script_command:
                        single_commands = script_command.split("\n")
                    else:
                        single_commands.append(script_command)
                    for command in single_commands:
                        self._log_time(result)
                        result.append(command)
        self._log_time(result)
        return "\n".join(result)

    def _log_time(self, result: list[str]) -> None:
        log_time = self.default_config.settings["logTime"]
        if log_time:
            result.append("backup_exec\t/bin/date +%s")

    def get_step(self, step: str) -> str:
        if self.backup_steps.get(step, ""):
            return self.backup_steps.get(step, "")
        return self.default_config.get_step(step)

    def get_enabled_actions(self) -> dict[str, bool]:
        merged_dict = self.default_config.enabled_actions.copy()
        merged_dict.update(self.enabled_actions)
        return merged_dict

    def add_action_content(self) -> None:
        for action, enabled in sorted(self.get_enabled_actions().items()):
            if enabled:
                commands = self.default_config.get_action(action)
                for step in commands:
                    self.backup_steps[step] += commands[step].strip() + "\n"
