#!/usr/bin/env python3

import os
import re
from typing import List, Tuple
from concurrent import futures

from rsnapshot_docker_compose_backup.container import Container
from rsnapshot_docker_compose_backup import docker
from rsnapshot_docker_compose_backup.utils import command


def get_binary() -> str:
    if command("docker compose").returncode == 0:
        return "docker compose"
    elif command("docker-compose").returncode == 0:
        return "docker-compose"
    else:
        raise Exception("Docker Compose is not installed")


def get_container_id(container: str, path: str) -> str:
    return command("{} ps -q {}".format(get_binary(), container), path=path).stdout


def container_runs(container_id: str) -> bool:
    if docker.ps(container_id):
        return True
    else:
        return False


def find_running_container(root_folder: str) -> List[Container]:
    all_container: List[Container] = []
    docker_dirs: List[str] = find_docker_dirs(root_folder)
    with futures.ProcessPoolExecutor() as pool:
        for service_list, directory in pool.map(get_services, docker_dirs):
            # container_list: List[str] = get_services(output)
            for service, container_id in service_list:
                # container_id = get_container_id(container, directory)[:12]
                if container_id and container_runs(container_id):
                    all_container.append(Container(directory, service, container_id))
    return all_container


def get_services(path: str) -> Tuple[List[Tuple[str, str]], str]:
    service_name: List[str] = command(
        "{} config --services".format(get_binary()), path=path
    ).stdout.splitlines()
    # Docker doesn't return it always in the same order
    service_name.sort()
    services: List[Tuple[str, str]] = []
    for service in service_name:
        container_id = get_container_id(service, path)[:12]
        services.append((service, container_id))
    return services, path


def find_docker_dirs(root_folder: str = os.getcwd()) -> List[str]:
    """Finds all docker-compose dirs in current sub folder
    :returns: a list of all folders"""
    dirs: List[str] = []
    docker_compose_files = [
        "compose.yaml",
        "compose.yml",
        "docker-compose.yaml",
        "docker-compose.yml",
    ]
    for tree_element in os.walk(root_folder):
        for docker_compose_file in docker_compose_files:
            if docker_compose_file in tree_element[2]:
                dirs.append(tree_element[0])
                break
    return dirs


def get_running_container(ps_out: str) -> List[str]:
    return get_container(ps_out, state="UP")


def get_column(column_nr: int, input_str: str):
    return re.sub(r"\s\s+", "  ", input_str).split("  ")[column_nr]


def get_container(ps_out: str, state: str | None = None) -> List[str]:
    all_container: List[str] = ps_out.splitlines()[2:]
    container: List[str] = []
    if not all_container:
        return []
    for line in all_container:
        up = get_column(2, line).upper()
        if not state or up == state.upper():
            container.append(get_column(0, line))
    return container
