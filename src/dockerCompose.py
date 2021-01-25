import os
import re
from typing import List, Tuple

from container import Container
from src.utils import command
from concurrent import futures


def find_running_container() -> List[Container]:
    all_container: List[Container] = []
    docker_dirs: List[str] = find_docker_dirs()
    with futures.ProcessPoolExecutor() as pool:
        for output, directory in pool.map(ps, docker_dirs):
            container_list: List[str] = get_running_container(output)
            for container in container_list:
                image = image_id(container, directory)
                all_container.append(Container(directory, container, image))
    return all_container


def ps(path: str) -> Tuple[str, str]:
    return command("docker-compose ps", path=path).stdout, path


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


def get_column(column_nr: int, input_str: str):
    return re.sub(r"\s\s+", "  ", input_str).split("  ")[column_nr]


def get_container(ps_out: str, state: str = None) -> List[str]:
    all_container = ps_out.splitlines()[2:]
    container = []
    if not all_container:
        return []
    for line in all_container:
        up = get_column(2, line).upper()
        if not state or up == state.upper():
            container.append(get_column(0, line))
    return container


def image_id(container_name: str, path: str):
    output = command("docker-compose images".format(container_name), path=path).stdout
    #The information about the services start at the third line and the 4. column contains the image id
    without_head: List[str] = output.splitlines()[2:]
    for service in without_head:
        if service.lower().startswith(container_name.lower()):
            return get_column(3, service)
    raise Exception("Cant find image for Service" + container_name)
