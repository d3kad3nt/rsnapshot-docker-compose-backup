import configparser
import os
import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import Any

from rsnapshot_docker_compose_backup.structure.volume import Volume
from rsnapshot_docker_compose_backup.utils.regex import CaseInsensitiveRe


class AbstractConfig(ABC):
    action_section = "actions"
    var_section = "vars"
    backup_order = (
        "runtime_backup",
        "pre_stop",
        "stop",
        "pre_backup",
        "backup",
        "post_backup",
        "restart",
        "post_restart",
    )

    def __init__(self, config_path: Path, name: str):
        self.enabled_actions: dict[str, bool] = {}
        self.backup_steps: dict[str, str] = {}
        self.vars: dict[str, str | list[Volume]] = {}
        for step in self.backup_order:
            self.backup_steps[step] = ""
        self._load_config_file(config_path, name)
        self._init_vars(str(config_path))

    def _init_vars(self, config_path: str) -> None:
        self.vars["$dockerComposeFile"] = config_path

    def _load_config_file(self, config_path: Path, section_name: str) -> None:
        section_name = section_name.lower()
        config_file = configparser.ConfigParser(allow_no_value=True)
        config_file.SECTCRE = CaseInsensitiveRe(
            re.compile(r"\[ *(?P<header>[^]]+?) *]")
        )  # type: ignore
        if os.path.isfile(config_path):
            config_file.read(config_path)
            if not config_file.sections():
                msg = f"The Config for {config_path} has no Sections"
                raise ValueError(msg)
        for step in self.backup_steps:
            if config_file.has_option(section_name, step):
                self.backup_steps[step] = (
                    config_file.get(section_name, step).strip() + "\n"
                )
        actions_section = self.actions_name(section_name)
        if config_file.has_section(actions_section):
            for action in config_file.options(actions_section):
                val = config_file.get(actions_section, action, fallback=None)
                use = val is None or val.lower() in {"true"}
                self.enabled_actions[action] = use
        vars_section = self.vars_name(section_name)
        if config_file.has_section(vars_section):
            for var in config_file.options(vars_section):
                val = config_file.get(vars_section, var)
                self.vars[f"${var}"] = val

    def _resolve_vars(self, cmd: str, variables: dict[str, str | list[Volume]]) -> str:
        for var, value in variables.items():
            if var.lower() in cmd.lower():
                replace_function = _replace_var.get(type(value))
                if not replace_function:
                    msg = f"Illegal Type for variable {var}: {type(value)}"
                    raise ValueError(msg)
                cmd = replace_function(cmd, var, value)
        return cmd

    @abstractmethod
    def get_step(self, step: str) -> str:
        pass

    @staticmethod
    def _create_subsection(super_section: str, sub_section: str) -> str:
        return f"{super_section}.{sub_section}"

    @staticmethod
    def actions_name(section_name: str) -> str:
        return AbstractConfig._create_subsection(
            section_name, AbstractConfig.action_section
        )

    @staticmethod
    def vars_name(section_name: str) -> str:
        return AbstractConfig._create_subsection(
            section_name, AbstractConfig.var_section
        )


def ireplace(old: str, new: str, text: str) -> str:
    idx = 0
    while idx < len(text):
        index_l = text.lower().find(old.lower(), idx)
        if index_l == -1:
            return text
        text = text[:index_l] + new + text[index_l + len(old) :]
        idx = index_l + len(new)
    return text


def _replace_list(cmd: str, var: str, val: list[list[Any] | str | Volume]) -> str:
    result: str = ""
    for i in val:
        result += str(_replace_var[type(i)](cmd, var, i)) + "\n"
    return result


def _replace_str(cmd: str, var: str, val: str) -> str:
    return ireplace(var, val, cmd)


def _replace_volume(cmd: str, var: str, val: Volume) -> str:
    tmp = _replace_str(cmd, var + ".name", val.name)
    tmp = _replace_str(tmp, var + ".path", val.path)
    return _replace_str(tmp, var, val.path)


_replace_var: dict[type, Callable[..., str]] = {
    list: _replace_list,
    str: _replace_str,
    Volume: _replace_volume,
}
