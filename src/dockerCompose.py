import os
import re
from typing import List

from container import Container
from src.utils import command


def find_running_container() -> List[Container]:
    all_container: List[Container] = []
    docker_dirs: List[str] = find_docker_dirs()
    for directory in docker_dirs:
        res = command("docker-compose ps", path=directory)
        container_list: List[str] = get_running_container(res.stdout)
        for container in container_list:
            all_container.append(Container(directory, container))
    return all_container


"""Finds all docker-compose dirs in current sub folder
:returns: a list of all folders
"""


def find_docker_dirs() -> List[str]:
    dirs: List[str] = []
    cwd: str = os.getcwd()
    for treeElement in os.walk(cwd):
        if "docker-compose.yml" in treeElement[2]:
            dirs.append(treeElement[0])
    return dirs


def get_running_container(ps_out: str) -> List[str]:
    return get_container(ps_out, state="UP")


def get_container(ps_out: str, state: str = None) -> List[str]:
    all_container = ps_out.splitlines()[2:]
    container = []
    if not all_container:
        return []
    for line in all_container:
        parts = re.sub(r"\s\s+", "  ", line).split("  ")
        up = parts[2].upper()
        if not state or up == state.upper():
            container.append(parts[0])
    return container
