#!/usr/bin/env python3

from dataclasses import dataclass
import os
from pathlib import Path
import re
from typing import List, Tuple
from concurrent import futures
import json

from rsnapshot_docker_compose_backup.container import Container
from rsnapshot_docker_compose_backup.utils import command


def get_binary() -> str:
    if command("docker compose").returncode == 0:
        return "docker compose"
    elif command("docker-compose").returncode == 0:
        return "docker-compose"
    else:
        raise Exception("Docker Compose is not installed")


def get_container_id(service_name: str, path: Path) -> str:
    return command(
        "{} ps --all -q {}".format(get_binary(), service_name), path=path
    ).stdout[:12]


def get_container_name(service_name: str, path: Path) -> str:
    stdout = command(
        "{} config --format json {}".format(get_binary(), service_name),
        path=path,
    ).stdout
    # print(f"stdout: {stdout} (End)")
    return str(json.loads(stdout)["services"][service_name]["container_name"])


def container_stopped(container_id: str) -> bool:
    status = command(
        [
            "docker",
            "ps",
            "-a",
            "--format",
            "{{ .Status }}",
            "-f",
            f"id={container_id}",
        ]
    )
    # print(status.stdout)
    return status.stdout.startswith("Exited")


def find_container(root_folder: Path) -> List[Container]:
    all_container: List[Container] = []
    docker_dirs: List[Path] = find_docker_dirs(root_folder)
    with futures.ProcessPoolExecutor() as pool:
        for service_list, directory in pool.map(get_services, docker_dirs):
            # container_list: List[str] = get_services(output)
            for container_info in service_list:
                if container_info.container_id:
                    all_container.append(
                        Container(
                            folder=directory,
                            service_name=container_info.service_name,
                            container_name=container_info.container_name,
                            container_id=container_info.container_id,
                            running=not container_stopped(container_info.container_id),
                        )
                    )
    return all_container


@dataclass
class ContainerInfo:
    service_name: str
    container_name: str
    container_id: str


def get_services(path: Path) -> Tuple[List[ContainerInfo], Path]:
    service_name: List[str] = command(
        "{} config --services".format(get_binary()), path=path
    ).stdout.splitlines()
    # Docker doesn't return it always in the same order
    service_name.sort()
    # print(service_name)
    services: List[ContainerInfo] = []
    for service in service_name:
        container_id = get_container_id(service, path)
        container_name = get_container_name(service, path)
        services.append(ContainerInfo(service, container_name, container_id))
    return services, path


def find_docker_dirs(root_folder: Path = Path(os.getcwd())) -> List[Path]:
    """Finds all docker-compose dirs in current sub folder
    :returns: a list of all folders"""
    dirs: List[Path] = []
    docker_compose_files = [
        "compose.yaml",
        "compose.yml",
        "docker-compose.yaml",
        "docker-compose.yml",
    ]
    for tree_element in os.walk(root_folder):
        for docker_compose_file in docker_compose_files:
            if docker_compose_file in tree_element[2]:
                dirs.append(Path(tree_element[0]))
                break
    return dirs


def get_running_container(ps_out: str) -> List[str]:
    return get_container(ps_out, state="UP")


def get_column(column_nr: int, input_str: str) -> str:
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
