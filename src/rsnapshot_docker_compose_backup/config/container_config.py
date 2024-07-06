from pathlib import Path
from typing import Dict, List, Optional, Union


from rsnapshot_docker_compose_backup.structure.volume import Volume
from rsnapshot_docker_compose_backup.config.abstract_config import AbstractConfig
from rsnapshot_docker_compose_backup.config.default_config import DefaultConfig


class ContainerConfig(AbstractConfig):
    def __init__(
        self,
        container_vars: Dict[str, Union[str, list[Volume]]],
        is_running: bool,
        config_file: Path,
        service_name: str,
    ):
        self.default_config: DefaultConfig = DefaultConfig.get_instance()
        super().__init__(config_file, service_name)
        for name, value in container_vars.items():
            self.vars[name] = value
        self._is_running = is_running
        self.add_action_content()

    def _all_vars(self) -> Dict[str, Union[str, List[Volume]]]:
        variables: Dict[str, Union[str, List[Volume]]] = {}
        variables.update(self.default_config.vars)
        variables.update(self.vars)
        return variables

    def output(self) -> Optional[str]:
        if self.default_config.settings["onlyRunning"] and not self._is_running:
            return None
        result: List[str] = []

        for step in self.backupOrder:
            backup_action = self.get_step(step)
            if backup_action:
                result.append("#{}".format(step))
                for line in backup_action.splitlines():
                    script_command = self._resolve_vars(line, self._all_vars()).strip(
                        "\n"
                    )
                    single_commands: List[str] = []
                    if "\n" in script_command:
                        single_commands = script_command.split("\n")
                    else:
                        single_commands.append(script_command)
                    for command in single_commands:
                        self._log_time(result)
                        result.append(command)
        self._log_time(result)
        return "\n".join(result)

    def _log_time(self, result: List[str]) -> None:
        log_time = self.default_config.settings["logTime"]
        if log_time:
            result.append("backup_exec\t/bin/date +%s")

    def get_step(self, step: str) -> str:
        if self.backup_steps.get(step, ""):
            return self.backup_steps.get(step, "")
        return self.default_config.get_step(step)

    def get_enabled_actions(self) -> Dict[str, bool]:
        merged_dict = self.default_config.enabled_actions.copy()
        merged_dict.update(self.enabled_actions)
        return merged_dict

    def add_action_content(self) -> None:
        for action, enabled in sorted(self.get_enabled_actions().items()):
            if enabled:
                commands = self.default_config.get_action(action)
                for step in commands:
                    self.backup_steps[step] += commands[step].strip() + "\n"
