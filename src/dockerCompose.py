import os
import re
from typing import List, Tuple

from container import Container
from src import docker
from src.utils import command
from concurrent import futures


def get_container_id(container: str, path: str) -> str:
    return command("docker-compose ps -q {}".format(container), path=path).stdout


def container_runs(container_id):
    if docker.ps(container_id):
        return True
    else:
        return False


def find_running_container() -> List[Container]:
    all_container: List[Container] = []
    docker_dirs: List[str] = find_docker_dirs()
    with futures.ProcessPoolExecutor() as pool:
        for container_list, directory in pool.map(get_services, docker_dirs):
            # container_list: List[str] = get_services(output)
            for container, container_id in container_list:
                # container_id = get_container_id(container, directory)[:12]
                if container_id and container_runs(container_id):
                    all_container.append(Container(directory, container, container_id))
    return all_container


def get_services(path: str) -> Tuple[List[Tuple[str, str]], str]:
    service_name = command("docker-compose config --services", path=path).stdout.splitlines()
    services = []
    for service in service_name:
        container_id = get_container_id(service, path)[:12]
        services.append((service, container_id))
    return services, path

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
