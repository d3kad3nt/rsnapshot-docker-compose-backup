from concurrent import futures
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import socket
from typing import Any, Optional

from rsnapshot_docker_compose_backup.structure.container import Container
from rsnapshot_docker_compose_backup.utils import command
from rsnapshot_docker_compose_backup.structure.volume import Volume


def inspect(container: str) -> Any:
    # converts docker inspect to json and return only first container,
    # because this works only with one container
    return json.loads(command("docker inspect {}".format(container)).stdout)[0]


def ps(container_id: Optional[str] = None) -> str:
    result = command("docker ps -a").stdout
    if container_id:
        for line in ps().splitlines():
            if line.startswith(container_id[:11]):
                return line
        return ""
    return result


def volumes(container_id: str) -> list[Volume]:
    result: list[Volume] = []
    container_info = inspect(container_id)
    for mount in container_info["Mounts"]:
        if mount["Type"] == "volume":
            result.append(Volume(mount["Name"], mount["Source"]))
    return sorted(result)


def image(container_id: str) -> str:
    container_info: str = ps(container_id)
    return get_column(1, container_info)


@dataclass
class HttpResponse:
    protocol_version: str
    status_code: int
    status_text: str
    headers: dict[str, str]
    json_body: Any


class Api:

    _docker_socket: Optional[socket.socket] = None

    @staticmethod
    def get(endpoint: str) -> HttpResponse:
        docker_socket = None
        if docker_socket is None:
            print("new socket")
            docker_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            docker_socket.connect("/run/docker.sock")
        else:
            print("reuse socket")
        docker_socket.send(
            f"GET {endpoint} HTTP/1.1\r\nHost:docker.sock\r\n\r\n".encode("utf-8")
        )
        return Api._parse_response(docker_socket)

    @staticmethod
    def _parse_response(sock: socket.socket) -> HttpResponse:
        message_start = b""
        while not message_start.endswith(b"\r\n\r\n"):
            chunk = sock.recv(1)
            message_start = message_start + chunk
        lines: list[str] = message_start.decode("utf-8").splitlines()
        status_line = lines[0]
        protocol_version = status_line.split(" ")[0]
        status_code = int(status_line.split(" ")[1])
        status_text = " ".join(status_line.split(" ")[2:])
        headers: dict[str, str] = {}
        for line in lines[1:]:
            split = line.split(":")
            if len(split) == 2:
                headers[split[0]] = split[1]
        body_length = int(headers["Content-Length"])
        body = sock.recv(body_length).decode("utf-8")
        return HttpResponse(
            protocol_version=protocol_version,
            status_code=status_code,
            status_text=status_text,
            headers=headers,
            json_body=json.loads(body),
        )


def get_version() -> str:
    return str(Api.get("/version").json_body["Version"])


def get_binary() -> str:
    if command("docker compose").returncode == 0:
        return "docker compose"
    if command("docker-compose").returncode == 0:
        return "docker-compose"

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


def find_container(root_folder: Path) -> list[Container]:
    all_container: list[Container] = []
    docker_dirs: list[Path] = find_docker_dirs(root_folder)
    with futures.ProcessPoolExecutor() as pool:
        for service_list, directory in pool.map(get_services, docker_dirs):
            # container_list: list[str] = get_services(output)
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


def get_services(path: Path) -> tuple[list[ContainerInfo], Path]:
    service_name: list[str] = command(
        "{} config --services".format(get_binary()), path=path
    ).stdout.splitlines()
    # Docker doesn't return it always in the same order
    service_name.sort()
    # print(service_name)
    services: list[ContainerInfo] = []
    for service in service_name:
        container_id = get_container_id(service, path)
        container_name = get_container_name(service, path)
        services.append(ContainerInfo(service, container_name, container_id))
    return services, path


def find_docker_dirs(root_folder: Path = Path(os.getcwd())) -> list[Path]:
    """Finds all docker-compose dirs in current sub folder
    :returns: a list of all folders"""
    dirs: list[Path] = []
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


def get_running_container(ps_out: str) -> list[str]:
    return get_container(ps_out, state="UP")


def get_column(column_nr: int, input_str: str) -> str:
    return re.sub(r"\s\s+", "  ", input_str).split("  ")[column_nr]


def get_container(ps_out: str, state: Optional[str] = None) -> list[str]:
    all_container: list[str] = ps_out.splitlines()[2:]
    container: list[str] = []
    if not all_container:
        return []
    for line in all_container:
        up = get_column(2, line).upper()
        if not state or up == state.upper():
            container.append(get_column(0, line))
    return container
